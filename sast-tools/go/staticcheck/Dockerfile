ARG GO_VERSION=1.23
FROM golang:${GO_VERSION}-alpine AS builder


ENV PATH="/root/go/bin:${PATH}"


RUN go install honnef.co/go/tools/cmd/staticcheck@latest


WORKDIR /staticcheck


COPY run_staticcheck.go .


RUN mkdir -p /output && \
    mkdir -p /tmp && chmod 1777 /tmp

RUN rm -rf /root/.cache


VOLUME ["/code"]
VOLUME ["/output"]

RUN go build -o run_staticcheck run_staticcheck.go


ENTRYPOINT ["/staticcheck/run_staticcheck"]
