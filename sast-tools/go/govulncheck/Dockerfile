ARG GO_VERSION=1.23
FROM golang:${GO_VERSION}-alpine AS builder

ENV PATH="/root/go/bin:${PATH}"

RUN go install golang.org/x/vuln/cmd/govulncheck@latest

WORKDIR /govulncheck

COPY run_govulncheck.go .

RUN mkdir -p /output && \
    mkdir -p /tmp && chmod 1777 /tmp

RUN rm -rf /root/.cache

RUN go build -o run_govulncheck run_govulncheck.go

VOLUME [ "/code", "/output" ]

CMD [ "/govulncheck/run_govulncheck" ]
