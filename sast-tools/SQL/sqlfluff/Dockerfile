ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-alpine AS builder

RUN pip install sqlfluff

# Set the working directory
WORKDIR /sqlfluff

# Add SQLFluff installation directory to PATH
ENV PATH="/root/.local/bin:${PATH}"

COPY run_sqlfluff.py .

RUN mkdir -p /output  \
    mkdir -p /tmp && chmod 1777 /tmp

# Clean up unnecessary files
RUN rm -rf /root/.cache /home/sqlfluff/.cache

VOLUME ["/code", "/output"]

# Run SQLFluff with the entry point script
ENTRYPOINT ["python", "run_sqlfluff.py"]
