ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-alpine AS builder

# Test all rules against all plugons
RUN pip install flake8 flake8-json \
    flake8-docstrings flake8-bugbear flake8-import-order flake8-quotes flake8-comprehensions \
    mccabe pep8-naming flake8-builtins flake8-colors flake8-annotations flake8-return  \
    flake8-print flake8-multiline-containers flake8-pytest-style flake8-variables-names

# Set the working directory
WORKDIR /flake

# Add pylint installation directory to PATH
ENV PATH="/root/.local/bin:${PATH}"

COPY run_flake.py .

RUN mkdir -p /output  \
    mkdir -p /tmp && chmod 1777 /tmp


# Clean up unnecessary files
RUN rm -rf /root/.cache /home/flake8/.cache

VOLUME ["/code"]
VOLUME [ "/output"]

# Run Pylint with the entry point script
ENTRYPOINT ["python", "run_flake.py"]
