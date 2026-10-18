from collections import deque
from pydantic import BaseModel, ConfigDict, ValidationError, Field
from lab_fw.core.errors import SchemaError
from enum import StrEnum
from lab_fw.api.client import ApiClient
import httpx
from lab_fw.core.errors import ApiError, JobDeadlineExceeded, WorkerDeadlineExceeded
from lab_fw.api.client import ensure_success
from lab_fw.core.retry import retry_call
import time

class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class Job(BaseModel):
    model_config = ConfigDict(
                                    strict=True,
                                    extra="forbid",
                                )
    method: HttpMethod = Field(strict=False)
    path: str
    timeout: float | None = None
    deadline_s: float | None = None
    payload: dict[str, object] | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    idempotency_key: str | None = None

def parse_job(data: dict[str, object]) -> Job:
    try:
        return Job.model_validate(data)
    except ValidationError as exc:
        raise SchemaError(f"Job schema validation failed: {exc}") from exc

class InMemoryQueue:
    def __init__(
                    self,
                    queue: deque[Job] | None = None,
                ) -> None:
        self._queue = queue if queue is not None else deque()

    def get(self) -> Job | None:
        return self._queue.popleft() if self._queue else None

    def put(self, job: Job) -> None:
        if isinstance(job, Job):
            self._queue.append(job)
        else:
            raise TypeError(f"Type mismatch '{type(job)}': expected type Job")
        
class Worker:
    def __init__(self, queue: InMemoryQueue, api_client: ApiClient, deadline_w: float | None = None) -> None:
        self._queue = queue
        self._api_client = api_client
        self.deadline_w = (
                                time.monotonic() + deadline_w
                                if deadline_w is not None
                                else None
                            )
    
    def _remaining_time(self, deadline: float, work: bool = False) -> float:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            if work:
                raise WorkerDeadlineExceeded("Worker deadline exceeded")
            raise JobDeadlineExceeded("Job deadline exceeded")
        return remaining

    def execute(self, 
                job: Job, 
                deadline: float | None = None,
                ) -> httpx.Response:
        kwargs = {}
        if self.deadline_w is not None:
           remaining_worker = self._remaining_time(self.deadline_w, True)
        else:
            remaining_worker = float('inf')
        if deadline is not None:
            remaining = self._remaining_time(deadline)
            timeout = min(remaining, remaining_worker) if job.timeout is None else min(job.timeout, remaining, remaining_worker)
            kwargs["timeout"] = timeout
        elif job.timeout is not None:
            kwargs["timeout"] = min(job.timeout, remaining_worker)
        if job.payload is not None:
            kwargs["json"] = job.payload.copy()
        kwargs["headers"] = job.headers.copy()
        if job.idempotency_key is not None:
            kwargs["headers"]["Idempotency-Key"] = job.idempotency_key

        match job.method:
            case HttpMethod.GET: 
                return self._api_client.get(job.path, **kwargs)
            case HttpMethod.POST: 
                return self._api_client.post(job.path, **kwargs)
            case _:
                raise NotImplementedError(f"{job.method} is not supported by ApiClient")

    def run_once(self) -> httpx.Response | None:
        if self.deadline_w is not None:
            self._remaining_time(self.deadline_w, True)
        job = self._queue.get()
        if job is None:
            return None
        
        deadline = (
                        time.monotonic() + job.deadline_s
                        if job.deadline_s is not None
                        else None
                    )

        def attempt() -> httpx.Response:
            if self.deadline_w is not None:
                self._remaining_time(self.deadline_w, True)
            if deadline is not None:
                self._remaining_time(deadline)

            return ensure_success(self.execute(job, deadline))


        try:
            response = retry_call(
                                    attempt,
                                    attempts=3,
                                    delay_s=0,
                                    retry_on=(ApiError,),
                                    retry_if = True,
                                    )
            if self.deadline_w is not None:
                self._remaining_time(self.deadline_w, True)
            if deadline is not None:
                self._remaining_time(deadline)
        except ApiError:
            if self.deadline_w is not None:
                self._remaining_time(self.deadline_w, True)
            if deadline is not None:
                self._remaining_time(deadline)
            raise

        return response
    
            
        
            
    