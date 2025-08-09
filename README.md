# 🚀 Full-Stack App Generator 🚀

This project is a powerful code generator that scaffolds a complete full-stack application, including a web frontend, a backend, a mobile app, and a full CI/CD pipeline with Docker. It's designed to accelerate development by automating the creation of boilerplate code and project structure based on a simple JSON configuration.

## ✨ Features

The generator creates a multi-platform application with a rich set of features out of the box.

### 🌐 Frontend (Angular)

- **Modern Angular Setup:** Standalone components, SCSS styling.
- **Component Library:** PrimeNG for a rich set of UI components.
- **Styling:** Tailwind CSS for utility-first styling.
- **State Management:** NGXS for robust and scalable state management.
- **API Integration:** Generates services for all entities to communicate with the backend.
- **Development Proxy:** Configures a proxy to the backend to avoid CORS issues.
- **Internationalization (i18n):** Uses `@ngx-translate` for multi-language support.
- **Testing:**
    - **Cypress:** For end-to-end testing.
    - **Storybook:** For component visualization and testing.
    - **Component Tests:** Generates basic `.spec.ts` files for all components.
- **Documentation:** Configured with Compodoc for generating project documentation.

### ⚙️ Backend (Spring Boot)

- **Build System:** Maven for dependency management.
- **Database:** PostgreSQL for robust data persistence.
- **API:** Generates a complete RESTful API for all entities.
- **Architecture:**
    - **DTO Pattern:** Decouples the API from the database entities.
    - **Service Layer:** For business logic.
- **ORM:** Spring Data JPA for data access.
- **Code Quality:** Uses Lombok to reduce boilerplate code.
- **Monitoring:** Exposes metrics for Prometheus via Spring Boot Actuator.

### 📱 Mobile (Flutter)

- **Cross-Platform:** Generates a Flutter application for both Android and iOS.
- **State Management:** Uses the Provider pattern for simple and effective state management.
- **API Integration:** Generates services to communicate with the backend API.
- **UI:** Creates basic list screens for all entities.

### 🐳 CI/CD (Docker)

- **Containerization:** Generates multi-stage `Dockerfile`s for the frontend and backend to produce lean, production-ready images.
- **Orchestration:** Creates a `docker-compose.yml` file to manage the entire application stack.
- **Services:**
    - **Nginx:** Acts as a reverse proxy for the frontend and backend.
    - **PostgreSQL:** The application database.
    - **MinIO:** S3-compatible object storage.
    - **Prometheus:** For collecting application metrics.
    - **Grafana:** For visualizing metrics, pre-configured with Prometheus as a data source.

## 🚀 How It Works

The project reads two main configuration files:

- `project.json`: Defines the basic project structure (e.g., app names, package names).
- `entities.json`: Contains the list of entities and their properties, which drives the code generation for all platforms.

The `main.py` script orchestrates the following generators:
- `ProjectInitializer`: Creates the basic directory structure.
- `FrontendGenerator`: Scaffolds the Angular web application.
- `BackendGenerator`: Scaffolds the Spring Boot backend application.
- `MobileGenerator`: Scaffolds the Flutter mobile application.
- `CiCdGenerator`: Creates the Dockerfiles and `docker-compose.yml`.

## ▶️ How to Run

### Prerequisites

- Python 3
- Docker and Docker Compose
- Flutter SDK (if you want to run the mobile app locally)
- Node.js and npm (for local frontend development)
- Java and Maven (for local backend development)

### Generating the Application

1.  Customize `project.json` and `entities.json` to define your application.
2.  Run the generator:
    ```bash
    python3 main.py
    ```
    This will create a new directory (specified by the `name` in `project.json`, e.g., `generated_app/`) containing the complete project.

### Running the Full Stack with Docker

Navigate to the generated project directory and run:
```bash
docker-compose up --build
```
This will build the Docker images and start all the services. The application will be available at `http://localhost`.

- **Web Frontend:** `http://localhost`
- **Backend API:** `http://localhost/api`
- **MinIO Console:** `http://localhost:9001`
- **Prometheus:** `http://localhost:9090`
- **Grafana:** `http://localhost:3000`

## 📄 License
MIT License
