ARG NODE_VERSION=23.9.0
ARG ALPINE_VERSION=3.21
ARG ESLINT_VERSION=9.29.0

FROM node:${NODE_VERSION}-alpine${ALPINE_VERSION}

# Install ESLint globally with specific version
RUN npm install -g eslint@${ESLINT_VERSION}

# Create a directory for ESLint files

# Copy the script and config to /eslint
COPY run_eslint.sh .
COPY eslint.config.js .
RUN chmod +x run_eslint.sh

# Expose the volumes for code and output
VOLUME [ "/code", "/output" ]

# Run ESLint as the entrypoint
ENTRYPOINT ["./run_eslint.sh"]
