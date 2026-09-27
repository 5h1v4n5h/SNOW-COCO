FROM nginx:alpine

# Remove default nginx site
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copy custom NGINX proxy configuration
COPY nginx.conf /etc/nginx/conf.d/enterprise-copilot.conf

# Copy React static build
COPY . /usr/share/nginx/html

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
