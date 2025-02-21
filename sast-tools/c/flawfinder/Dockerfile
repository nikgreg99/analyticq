ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-alpine AS builder

RUN pip install flawfinder


# Set the working directory
WORKDIR /flawfinder

# Add pylint installation directory to PATH
ENV PATH="/root/.local/bin:${PATH}"

COPY run_flawfinder.py .

RUN mkdir -p /output  \
    mkdir -p /tmp && chmod 1777 /tmp


# Clean up unnecessary files
RUN rm -rf /root/.cache /home/flawfinder/.cache

VOLUME ["/code"]
VOLUME [ "/output"]

# Run Pylint with the entry point script
ENTRYPOINT ["python", "run_flawfinder.py"]
