ARG GO_VERSION=1.23
ARG GOSEC_VERSION=2.22.2  # Sostituisci con la versione desiderata

FROM golang:${GO_VERSION}-alpine AS builder

ENV PATH="/root/go/bin:${PATH}"

RUN apk add --no-cache wget \
    && wget -O - -q https://raw.githubusercontent.com/securego/gosec/master/install.sh | sh -s ${GOSEC_VERSION}

WORKDIR /gosec

COPY run_gosec.go .

RUN mkdir -p /output /tmp && chmod 1777 /tmp \
    && rm -rf /root/.cache

VOLUME ["/code", "/output"]

RUN go build -o run_gosec run_gosec.go

ENTRYPOINT ["/gosec/run_gosec"]
