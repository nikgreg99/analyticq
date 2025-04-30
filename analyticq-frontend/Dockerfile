ARG NODE_VERSION=18.20-alpine3.21
ARG NGINX_INGRESS_VERSION=4.0.1-alpine

FROM node:${NODE_VERSION}

WORKDIR /frontend

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM nginx/nginx/nginx-ingress${NGINX_INGRESS_VERSION}

COPY --from=build /app/dist /usr/share/nginx/html

# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
