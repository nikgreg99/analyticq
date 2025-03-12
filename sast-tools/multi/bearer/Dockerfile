ARG UBUNTU_VERSION=24.10

FROM ubuntu:${UBUNTU_VERSION}

# Update the package lists and install required packages
RUN apt-get update && \
    apt-get install -y ca-certificates apt-transport-https curl && \
    update-ca-certificates && \
    echo "deb [trusted=yes] https://apt.fury.io/bearer/ /" | tee -a /etc/apt/sources.list.d/fury.list && \
    apt-get update && \
    apt-get install -y bearer

# Set working directory
WORKDIR /bearer

# Copy the script and make it executable
COPY run_bearer.sh .
RUN chmod +x run_bearer.sh

# Set the volumes
VOLUME [ "/code", "/output" ]

# Set the entry point to the script
ENTRYPOINT ["/bearer/run_bearer.sh"]
