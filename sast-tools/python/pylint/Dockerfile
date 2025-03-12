ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-alpine AS builder

RUN pip install pylint

# Set the working directory
WORKDIR /pylint

# Add pylint installation directory to PATH
ENV PATH="/root/.local/bin:${PATH}"

COPY run_pylint.py .

RUN mkdir -p /output  \
    mkdir -p /tmp && chmod 1777 /tmp


# Clean up unnecessary files
RUN rm -rf /root/.cache /home/pylint/.cache

VOLUME ["/code", "/output"]

# Run Pylint with the entry point script
ENTRYPOINT ["python", "run_pylint.py"]
