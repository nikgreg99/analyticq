ARG RUBY_VERSION=3.2
ARG ALPINE_VERSION=3.20

FROM ruby:${RUBY_VERSION}-alpine AS build

# Install dependencies, including dos2unix
RUN apk add --no-cache wget git curl dos2unix bash \
    && gem install rubocop \
    && apk del bash

WORKDIR /rubocop
COPY run_rubocop.sh .
RUN mkdir -p /output

RUN dos2unix /rubocop/run_rubocop.sh \
    && chmod +x /rubocop/run_rubocop.sh

VOLUME [ "/code", "/output" ]

ENTRYPOINT [ "/rubocop/run_rubocop.sh" ]
