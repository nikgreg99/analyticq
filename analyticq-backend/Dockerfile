ARG PYTHON_VERSION=3.12  # Usa una versione stabile

FROM python:${PYTHON_VERSION}-slim AS build

# Mantieni le variabili d'ambiente
ENV PYTHONDONWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

ENV ANALYTICQ_BACKEND_HOST="0.0.0.0"
ENV ANALYTICQ_BACKEND_PORT=8000
ENV ANALYTICQ_BACKEND_PROFILE="dev"

WORKDIR /app

# Creazione del virtual environment
RUN python -m venv /venv

# Imposta il PATH per usare il venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Secondo stage
FROM python:${PYTHON_VERSION}-slim AS runtime

# Mantieni le variabili d'ambiente
ENV PYTHONDONWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

ENV ANALYTICQ_BACKEND_HOST="0.0.0.0"
ENV ANALYTICQ_BACKEND_PORT=8000
ENV ANALYTICQ_BACKEND_PROFILE="dev"

# Copia il virtual environment dal build stage
COPY --from=build /venv /venv

# Imposta il PATH per usare il venv
ENV PATH="/venv/bin:$PATH"

COPY analyticq/ .

EXPOSE 8000

CMD ["python", "start.py"]
