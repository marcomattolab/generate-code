import os
import json
from utils import run_cmd

class CiCdGenerator:
    def __init__(self, root_dir, project_config):
        self.root_dir = root_dir
        self.project_config = project_config

    def generate(self):
        self._log("Starting CI/CD generation...")
        self._generate_backend_dockerfile()
        self._generate_frontend_dockerfile()
        self._generate_nginx_config()
        self._generate_prometheus_config()
        self._generate_grafana_config()
        self._generate_docker_compose()
        self._log("CI/CD generation complete.")

    def _generate_grafana_config(self):
        """Generates Grafana configuration files."""
        grafana_path = os.path.join(self.root_dir, "grafana", "provisioning", "datasources")
        os.makedirs(grafana_path, exist_ok=True)

        datasource_path = os.path.join(grafana_path, "datasource.yml")

        datasource_content = """
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
"""

        with open(datasource_path, "w") as f:
            f.write(datasource_content)

    def _generate_prometheus_config(self):
        """Generates a prometheus.yml file."""
        prometheus_path = os.path.join(self.root_dir, "prometheus")
        os.makedirs(prometheus_path, exist_ok=True)

        prometheus_config_path = os.path.join(prometheus_path, "prometheus.yml")

        prometheus_config_content = """
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'spring-boot-app'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['backend:8080']
"""

        with open(prometheus_config_path, "w") as f:
            f.write(prometheus_config_content)

    def _generate_docker_compose(self):
        """Generates a docker-compose.yml file for the entire application stack."""
        compose_path = os.path.join(self.root_dir, "docker-compose.yml")

        compose_content = """
version: '3.8'

services:
  database:
    image: postgres:15-alpine
    container_name: my_database
    environment:
      POSTGRES_DB: mydatabase
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  minio:
    image: minio/minio:RELEASE.2023-09-07T22-05-05Z
    container_name: my_minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    command: server /data --console-address ":9001"

  prometheus:
    image: prom/prometheus:v2.47.0
    container_name: my_prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:10.1.1
    container_name: my_grafana
    depends_on:
      - prometheus
    volumes:
      - ./grafana/provisioning/:/etc/grafana/provisioning/
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"

  backend:
    build:
      context: ./backend
    container_name: my_backend
    depends_on:
      - database
      - minio
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://database:5432/mydatabase
      SPRING_DATASOURCE_USERNAME: myuser
      SPRING_DATASOURCE_PASSWORD: mypassword
      MINIO_URL: http://minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    ports:
      - "8080:8080"

  nginx:
    build:
      context: ./frontend/app
    container_name: my_nginx
    depends_on:
      - backend
    ports:
      - "80:80"

volumes:
  postgres_data:
  minio_data:
  prometheus_data:
  grafana_data:
"""

        with open(compose_path, "w") as f:
            f.write(compose_content)

    def _generate_nginx_config(self):
        """Generates a custom Nginx configuration file."""
        frontend_path = os.path.join(self.root_dir, self.project_config["frontend"], self.project_config["app"])
        nginx_conf_path = os.path.join(frontend_path, "nginx.conf")

        nginx_conf_content = """
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html index.htm;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

        with open(nginx_conf_path, "w") as f:
            f.write(nginx_conf_content)

    def _generate_frontend_dockerfile(self):
        """Generates a Dockerfile for the frontend Angular application."""
        frontend_path = os.path.join(self.root_dir, self.project_config["frontend"], self.project_config["app"])
        dockerfile_path = os.path.join(frontend_path, "Dockerfile")

        dockerfile_content = f"""
# Stage 1: Build the application
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:1.25-alpine
COPY --from=build /app/dist/{self.project_config["app"]}/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
"""

        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)

    def _generate_backend_dockerfile(self):
        """Generates a Dockerfile for the backend Spring Boot application."""
        backend_path = os.path.join(self.root_dir, self.project_config["backend"])
        dockerfile_path = os.path.join(backend_path, "Dockerfile")

        dockerfile_content = """
# Stage 1: Build the application with Maven
FROM maven:3.8-jdk17-alpine AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn clean install

# Stage 2: Create the final image
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
"""

        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)

    def _log(self, message):
        print(f"[CiCdGenerator] {message}")
