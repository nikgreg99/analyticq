ARG RUBY_VERSION=3.2
ARG ALPINE_VERSION=3.20

FROM ruby:${RUBY_VERSION}-alpine AS build

# Install dependencies, including dos2unix
RUN apk add --no-cache wget git curl dos2unix bash \
    && gem install brakeman \
    && apk del bash

WORKDIR /brakeman

COPY run_brakeman.sh .
RUN mkdir -p /output

RUN dos2unix /brakeman/run_brakeman.sh \
    && chmod +x /brakeman/run_brakeman.sh

VOLUME [ "/code", "/output" ]

ENTRYPOINT [ "/brakeman/run_brakeman.sh" ]
