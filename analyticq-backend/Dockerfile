ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS build

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV ANALYTICQ_BACKEND_HOST="0.0.0.0" \
    ANALYTICQ_BACKEND_PORT=8000 \
    ANALYTICQ_BACKEND_PROFILE="dev"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc-dev libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"


COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# STAGE 2: Runtime
FROM python:${PYTHON_VERSION}-slim AS runtime


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV ANALYTICQ_BACKEND_HOST="0.0.0.0" \
    ANALYTICQ_BACKEND_PORT=8000 \
    ANALYTICQ_BACKEND_PROFILE="dev" \
    ANALYTICQ_USER=analyticq


RUN useradd --create-home  ${ANALYTICQ_USER}
WORKDIR /app
USER ${ANALYTICQ_USER}

COPY --from=build /venv /venv
ENV PATH="/venv/bin:$PATH"

COPY .  .
EXPOSE ${ANALYTICQ_BACKEND_PORT}

CMD ["python", "start.py"]
