ARG JAVA_VERSION=21
FROM openjdk:${JAVA_VERSION}-jdk-slim

ENV CHECKSTYLE_VERSION=10.21.3
ENV PATH="/checkstyle:$PATH"

# Install necessary packages and clean up
RUN apt-get update && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and install Checkstyle
RUN wget -O checkstyle-${CHECKSTYLE_VERSION}-all.jar https://github.com/checkstyle/checkstyle/releases/download/checkstyle-${CHECKSTYLE_VERSION}/checkstyle-${CHECKSTYLE_VERSION}-all.jar && \
    mkdir -p /checkstyle && \
    mv checkstyle-${CHECKSTYLE_VERSION}-all.jar /checkstyle/checkstyle.jar && \
    echo '#!/bin/bash\njava -jar /checkstyle/checkstyle.jar "$@"' > /checkstyle/checkstyle && \
    chmod +x /checkstyle/checkstyle

# Set the working directory
WORKDIR /checkstyle

# Copy the run_checkstyle.sh script and make it executable
COPY run_checkstyle.sh .
COPY config.xml .
RUN chmod +x run_checkstyle.sh

# Define volumes for code and output
VOLUME ["/code", "/output"]

# Set the entrypoint to the run_checkstyle.sh script
ENTRYPOINT ["./run_checkstyle.sh"]
