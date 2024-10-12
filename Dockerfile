# syntax=docker/dockerfile:1
FROM python:3.12-slim AS venv

LABEL maintainer="Jan Willhaus <mail@janwillhaus.de>"

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.2

WORKDIR /src
COPY pyproject.toml poetry.lock ./

RUN set -e; \
    pip install -U --no-cache-dir pip "poetry~=$POETRY_VERSION"; \
    python -m venv /venv; \
    . /venv/bin/activate; \
    poetry install \
        --no-interaction \
        --no-directory \
        --no-root \
        --only main

FROM python:3.12-slim

ENV PATH=/venv/bin:$PATH

RUN set -e; \
    apt-get update; \
    apt-get install -y --no-install-recommends 'tini=0.19.*' 'libsndfile1=1.*'; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

COPY --from=venv /venv /venv
COPY ./drmeter /drmeter

VOLUME [ "/archive" ]

ENTRYPOINT [ "tini", "--", "python", "-m", "drmeter"]
CMD [ "--help" ]
