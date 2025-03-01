ARG UBUNTU_VERSION=22.04
FROM ubuntu:${UBUNTU_VERSION}

# Set non-interactive mode for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies and cppcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends cppcheck && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /cppcheck

# Copy the run script into the container
COPY run_cppcheck.sh .
RUN chmod +x run_cppcheck.sh

VOLUME [ "/code", "/output" ]

# Set entrypoint to the script
ENTRYPOINT ["./run_cppcheck.sh"]
