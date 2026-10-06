FROM python:3.11-slim AS base

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests

FROM base AS local

COPY avast-root.crt /usr/local/share/ca-certificates/avast-root.crt

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "setuptools>=68" wheel
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt
RUN pip install --no-cache-dir --no-build-isolation -e ".[dev_slim]"

CMD ["pytest", "-m", "not ui and not selenium", "-q", "--tb=line", "-n", "auto"]

FROM base AS ci

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "setuptools>=68" wheel
RUN pip install --no-cache-dir --no-build-isolation -e ".[dev]"
#RUN playwright install --with-deps chromium

CMD ["pytest", "-m", "not ui and not selenium", "-q", "--tb=line", "-n", "auto"]
