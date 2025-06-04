ARG NODE_VERSION=23.9.0
ARG ALPINE_VERSION=3.21
ARG ESLINT_VERSION=8.57.1

FROM node:${NODE_VERSION}-alpine${ALPINE_VERSION}

# Install ESLint globally
RUN npm install  eslint --global

# Create a directory for ESLint files (outside of /code)
WORKDIR /eslint

# Copy the script and config to /eslint
COPY run_eslint.sh .
COPY eslint.config.js .
RUN chmod +x run_eslint.sh

# Expose the volumes for code and output
VOLUME [ "/code", "/output" ]

# Run ESLint as the entrypoint
ENTRYPOINT ["./run_eslint.sh"]
