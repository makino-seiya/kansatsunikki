FROM node:20.19-bullseye as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Update npm to v11 to avoid optional deps bug and install dependencies deterministically
RUN npm install -g npm@11 \
  && npm --version \
  && npm ci --ignore-scripts

# Copy application code and run project prepare (postinstall)
COPY . .
RUN npm run postinstall \
  && npm run build

FROM node:20.19-bullseye as runner
WORKDIR /app

# Copy only built output and minimal runtime files
COPY --from=builder /app/.output /app/.output
COPY --from=builder /app/package*.json /app/

ENV NODE_ENV=production
EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]