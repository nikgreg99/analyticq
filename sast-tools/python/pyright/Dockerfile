ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-alpine AS builder

RUN apk add --no-cache nodejs npm

# Test all rules against all plugis
RUN pip install pyright

# Set the working directory
WORKDIR /pyright

# Add pylint installation directory to PATH
ENV PATH="/root/.local/bin:${PATH}"

ENV PYRIGHT_PYTHON=/usr/local/bin/python3.11

COPY run_pyright.py .
COPY pyrightconfig.json .

RUN mkdir -p /output  \
    mkdir -p /tmp && chmod 1777 /tmp


# Clean up unnecessary files
RUN rm -rf /root/.cache /home/pyright/.cache

VOLUME ["/code"]
VOLUME [ "/output"]

# Run Pylint with the entry point script
ENTRYPOINT ["python", "run_pyright.py"]
