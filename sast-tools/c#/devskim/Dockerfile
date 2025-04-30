ARG DOTNET_VERSION=8

FROM bitnami/dotnet-sdk:${DOTNET_VERSION} AS builder

ENV PATH="/root/.dotnet/tools:${PATH}"

RUN dotnet tool install --global Microsoft.CST.DevSkim.CLI

WORKDIR /devsim

COPY run_devskim.sh .

RUN mkdir -p /output && \
    mkdir -p /tmp && chmod 1777 /tmp

RUN rm -rf /root/.local/share/NuGet

VOLUME [ "/code", "/output" ]

RUN chmod +x run_devskim.sh

ENTRYPOINT [ "/devskim/run_devskim.sh" ]
