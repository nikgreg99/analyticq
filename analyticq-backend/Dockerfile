# Stage 1: Build Stage
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS build

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set application profile and host/port configurations
ENV ANALYTICQ_BACKEND_HOST="0.0.0.0" \
    ANALYTICQ_BACKEND_PORT=8000 \
    ANALYTICQ_BACKEND_PROFILE="dev"

WORKDIR /analyticq-backend

# Install dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc-dev libffi-dev libssl-dev git\
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime Stage
FROM python:${PYTHON_VERSION}-slim AS runtime

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set application profile and host/port configurations
ENV ANALYTICQ_BACKEND_HOST="0.0.0.0" \
    ANALYTICQ_BACKEND_PORT=8000 \
    ANALYTICQ_BACKEND_PROFILE="dev" \
    ANALYTICQ_USER=analyticq

# Create a new user for running the application
RUN useradd --create-home ${ANALYTICQ_USER}

# Set working directory
WORKDIR /analyticq-backend

# Switch to the new user
USER ${ANALYTICQ_USER}

# Copy the virtual environment from the build stage
COPY --from=build /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy the backend source code
COPY . .

# Expose the backend port
EXPOSE ${ANALYTICQ_BACKEND_PORT}

# Start the application
CMD ["python", "start.py"]
