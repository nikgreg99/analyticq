ARG RUBY_VERSION=3.2
ARG ALPINE_VERSION=3.20

# --- Build stage ---
FROM ruby:${RUBY_VERSION}-alpine AS build

RUN apk add --no-cache \
    bash \
    build-base \
    libffi-dev \
    yaml-dev \
    zlib-dev \
    git \
    curl \
    dos2unix \
    && gem install rubocop \
    && apk del build-base libffi-dev yaml-dev zlib-dev


WORKDIR /rubocop
COPY run_rubocop.sh .
RUN dos2unix run_rubocop.sh && chmod +x run_rubocop.sh

# --- Runtime stage ---
FROM ruby:${RUBY_VERSION}-alpine

RUN apk add --no-cache dos2unix

# Copy gems and script from build
COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /rubocop /rubocop

VOLUME [ "/code", "/output" ]
ENTRYPOINT [ "/rubocop/run_rubocop.sh" ]
