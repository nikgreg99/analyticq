ARG PHP_VERSION=8.2

FROM php:${PHP_VERSION}-cli-alpine AS build

ENV COMPOSER_HOME="/composer"
ENV PATH="$COMPOSER_HOME/vendor/bin:$PATH"
ENV PHPSTAN_VERSION=2.1.5

# Installa le dipendenze e PHPStan
RUN apk add --no-cache wget git unzip curl dos2unix \
    && docker-php-ext-install opcache \
    && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer global require phpstan/phpstan:^${PHPSTAN_VERSION} \
    && composer clear-cache

# Imposta la directory di lavoro
WORKDIR /phpstan
RUN mkdir -p /output

# Copia file e correggi i permessi
COPY run_phpstan.sh  .
COPY phpstan.neon .
RUN chmod +x /phpstan/run_phpstan.sh && dos2unix /phpstan/run_phpstan.sh


# Monta i volumi per il codice
VOLUME [ "/code", "/output" ]

# Esegue lo script
ENTRYPOINT  [ "/phpstan/run_phpstan.sh" ]
