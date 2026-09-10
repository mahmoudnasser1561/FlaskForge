FROM node:22-alpine
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["sh", "-c", "cp -rf dist/. /output/"]
