FROM node:20.19-bullseye

WORKDIR /app

# Copy package files
COPY package*.json ./

# Update npm to v11 to avoid optional deps bug and install dependencies deterministically
RUN npm install -g npm@11 \
  && npm --version \
  && npm ci --ignore-scripts

# Copy application code and run project prepare (postinstall)
COPY . .
RUN npm run postinstall

# Expose port
EXPOSE 3000

# Start development server with proper host binding
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]