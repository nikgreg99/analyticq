ARG PYTHON_VERSION = 3.13

FROM python:${PYTHON_VERSION}-slim AS build

ENV PYTHONDONWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

ENV ANALYTICQ_BACKEND_HOST="0.0.0.0"
ENV ANALYTICQ_BACKEND_PORT=8000
ENV ANALYTICQ_BACKEND_PROFILE="dev"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

COPY --from=build /usr/local/lib/python${PYTHON_VERSION}/site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY analyticq/ .

EXPOSE $ANALYTICQ_BACKEND_PORT

CMD [ "python", "start.py" ]
