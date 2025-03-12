ARG JAVA_VERSION=21

FROM openjdk:${JAVA_VERSION}-jdk-slim

ENV CHECKSTYLE_VERSION=10.21.4
ENV PATH="/checkstyle:$PATH"

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update -o Acquire::Check-Valid-Until=false && \
    apt-get install -y wget

RUN apt-get update && apt-get install -y wget \
    && wget -O /checkstyle.jar https://github.com/checkstyle/checkstyle/releases/download/checkstyle-${CHECKSTYLE_VERSION}/checkstyle-${CHECKSTYLE_VERSION}-all.jar \
    && mkdir -p /checkstyle \
    && mv /checkstyle.jar /checkstyle/ \
    && apt-get clean

WORKDIR /checkstyle

COPY run_checkstyle.sh .
RUN chmod +x run_checkstyle.sh

VOLUME [ "/code", "/output"]

ENTRYPOINT [ "./run_checkstyle.sh" ]
