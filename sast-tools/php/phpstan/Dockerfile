ARG PHP_VERSION=8.2

FROM php:${PHP_VERSION}-cli-alpine AS build

ENV COMPOSER_HOME="/composer"
ENV PATH="$COMPOSER_HOME/vendor/bin:$PATH"
ENV PHPSTAN_VERSION=2.1.5

# Install dependencies, including dos2unix
RUN apk add --no-cache wget git unzip curl dos2unix \
    && docker-php-ext-install opcache \
    && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer global require phpstan/phpstan:^${PHPSTAN_VERSION} \
    && composer clear-cache

# Set the working directory
WORKDIR /phpstan
RUN mkdir -p /output

# Copy files and adjust permissions
COPY run_phpstan.sh .
COPY phpstan.neon .

# Convert line endings and set execute permissions
RUN dos2unix /phpstan/run_phpstan.sh \
    && chmod +x /phpstan/run_phpstan.sh

# (Optional) Remove dos2unix to reduce image size
RUN apk del dos2unix

# Define volumes for code and output
VOLUME ["/code", "/output"]

# Set the entry point to the script
ENTRYPOINT ["/phpstan/run_phpstan.sh"]
