ARG JAVA_VERSION=21


FROM openjdk:${JAVA_VERSION}-jdk-slim

ENV SPOTBUGS_VERSION=4.9.1
ENV MAVEN_VERSION=3.9.10
ENV PATH="/spotbugs/bin:/maven/bin:$PATH"

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update -o Acquire::Check-Valid-Until=false && \
    apt-get install -y wget unzip


RUN apt-get update && apt-get install -y wget unzip \
    && wget https://github.com/spotbugs/spotbugs/releases/download/${SPOTBUGS_VERSION}/spotbugs-${SPOTBUGS_VERSION}.zip \
    && unzip spotbugs-${SPOTBUGS_VERSION}.zip -d / \
    && mv /spotbugs-${SPOTBUGS_VERSION} /spotbugs \
    && rm spotbugs-${SPOTBUGS_VERSION}.zip \
    && apt-get clean

# Install Maven
RUN wget https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz \
    && tar -xzf apache-maven-${MAVEN_VERSION}-bin.tar.gz -C / \
    && mv /apache-maven-${MAVEN_VERSION} /maven \
    && rm apache-maven-${MAVEN_VERSION}-bin.tar.gz

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /spotbugs

COPY run_spotbugs.sh .
RUN chmod +x run_spotbugs.sh

VOLUME [ "/code", "/output"]

ENTRYPOINT [ "./run_spotbugs.sh" ]
