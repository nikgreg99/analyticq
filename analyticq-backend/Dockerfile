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

# Install dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc-dev libffi-dev libssl-dev git \
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime Stage
FROM python:${PYTHON_VERSION}-slim AS runtime

# Set environment variables for Python and app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ANALYTICQ_BACKEND_HOST="0.0.0.0" \
    ANALYTICQ_BACKEND_PORT=8000 \
    ANALYTICQ_BACKEND_PROFILE="prod" \
    ANALYTICQ_USER=analyticq

# Install necessary system packages and Docker CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg lsb-release git \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update && apt-get install -y --no-install-recommends docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Create user (no need for docker group with DinD)
RUN useradd --create-home --shell /bin/bash ${ANALYTICQ_USER}

WORKDIR /analyticq-backend

# Copy virtual environment from build stage
COPY --from=build /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy project files and give proper ownership
COPY --chown=${ANALYTICQ_USER}:${ANALYTICQ_USER} analyticq ./analyticq/.
COPY --chown=${ANALYTICQ_USER}:${ANALYTICQ_USER} config ./config/.
COPY --chown=${ANALYTICQ_USER}:${ANALYTICQ_USER} requirements.txt ./
COPY --chown=${ANALYTICQ_USER}:${ANALYTICQ_USER} start.py ./

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER ${ANALYTICQ_USER}

# Expose the backend port
EXPOSE ${ANALYTICQ_BACKEND_PORT}

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${ANALYTICQ_BACKEND_PORT}/health || exit 1

# Start the application
ENTRYPOINT ["/entrypoint.sh"]
