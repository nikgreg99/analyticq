ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-alpine AS builder

RUN pip install bandit

# Set the working directory
WORKDIR /bandit

COPY bandit.yaml .
COPY run_bandit.py .

RUN mkdir -p /output

# Clean up unnecessary files
RUN rm -rf /root/.cache /home/bandit/.cache

VOLUME ["/code", "/output"]

# Run Bandit with the entry point script
ENTRYPOINT ["python", "run_bandit.py", "/code"]
