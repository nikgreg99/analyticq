ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-alpine AS builder

RUN pip install njsscan

# Set the working directory
WORKDIR /njsscan

COPY run_njsscan.py .

RUN mkdir -p /output

# Clean up unnecessary files
RUN rm -rf /root/.cache /home/njsscan/.cache

VOLUME ["/code", "/output"]

# Run nodejsscan with the entry point script
ENTRYPOINT ["python", "run_njsscan.py"]
