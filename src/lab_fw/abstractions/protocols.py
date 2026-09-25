from typing import Protocol, runtime_checkable 

@runtime_checkable
class HttpClientProtocol(Protocol):
    def get(self, path, **kwargs):
        ...

    def post(self, path, **kwargs):
        ...

    def close(self):
        ...


