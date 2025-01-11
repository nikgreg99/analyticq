FROM python:3.11-slim AS build

ENV PYTHONDONWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

ENV HOST="0.0.0.0"
ENV PORT=8000
ENV PROFILE="dev"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime

ENV PYTHONDONWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY analyticq/ .

EXPOSE $ANALYTIC_BACKEND_PORT

CMD [ "sh" "-c" "uvicorn analyticq.app:create_app --host ${ANALYTIC_BACKEND_HOST} --port ${ANALYTIC_BACKEND_PORT} --factory" ]
