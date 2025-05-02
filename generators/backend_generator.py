import os
import json
from utils import run_cmd

class BackendGenerator:
    def __init__(self, root_dir, entities_file, project_config):
        self.root_dir = root_dir
        self.entities_file = entities_file
        self.project_config = project_config

    def generate(self):
        backend_path = os.path.join(self.root_dir, self.project_config["backend"])
        os.makedirs(backend_path, exist_ok=True)

        # Step 1: Creazione di una struttura base Spring Boot con dipendenze
        self._create_basic_structure(backend_path)

        # Step 2: Creazione delle entità JPA, repository, controller e service per ogni entità nel file JSON
        self._generate_entities_and_services(backend_path)

    def _create_basic_structure(self, path):
        """Scarica e decomprime il progetto Spring Boot base"""
        self._log("Creating Spring Boot base structure...")
        run_cmd("curl https://start.spring.io/starter.zip -d dependencies=web,data-jpa,h2 -o app.zip", cwd=path)
        run_cmd("unzip app.zip -d .", cwd=path)
        os.remove(os.path.join(path, "app.zip"))

    def _generate_entities_and_services(self, path):
        """Genera entità JPA, repository, controller, e service da entities.json"""
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]

        src_path = os.path.join(path, "src", "main", "java", *self.project_config["backend_package"].split("."))
        os.makedirs(src_path, exist_ok=True)

        for entity in entities:
            entity_name = entity["name"]
            entity_name_lower = entity_name.lower()

            # Creazione entità JPA
            self._generate_entity(entity, src_path, entity_name, entity_name_lower)

            # Creazione Repository JPA
            self._generate_repository(entity, src_path, entity_name, entity_name_lower)

            # Creazione Service
            self._generate_service(entity, src_path, entity_name, entity_name_lower)

            # Creazione Controller
            self._generate_controller(entity, src_path, entity_name, entity_name_lower)

    def _generate_entity(self, entity, src_path, entity_name, entity_name_lower):
        """Genera una classe Entity JPA per l'entità"""
        entity_path = os.path.join(src_path, "model")
        os.makedirs(entity_path, exist_ok=True)

        entity_fields = "\n".join([f"    private {col['type']} {col['name']};" for col in entity["columns"]])

        with open(os.path.join(entity_path, f"{entity_name}.java"), "w") as f:
            f.write(f"""
package {self.project_config["backend_package"]}.model;

import javax.persistence.*;

@Entity
@Table(name = "{entity_name_lower}")
public class {entity_name} {{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    {entity_fields}

    // Getters and setters
}}
""")

    def _generate_repository(self, entity, src_path, entity_name, entity_name_lower):
        """Genera un repository JPA per l'entità"""
        repo_path = os.path.join(src_path, "repository")
        os.makedirs(repo_path, exist_ok=True)

        with open(os.path.join(repo_path, f"{entity_name}Repository.java"), "w") as f:
            f.write(f"""
package {self.project_config["backend_package"]}.repository;

import {self.project_config["backend_package"]}.model.{entity_name};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface {entity_name}Repository extends JpaRepository<{entity_name}, Long> {{
}}
""")

    def _generate_service(self, entity, src_path, entity_name, entity_name_lower):
        """Genera un service per l'entità"""
        service_path = os.path.join(src_path, "service")
        os.makedirs(service_path, exist_ok=True)

        with open(os.path.join(service_path, f"{entity_name}Service.java"), "w") as f:
            f.write(f"""
package {self.project_config["backend_package"]}.service;

import {self.project_config["backend_package"]}.model.{entity_name};
import {self.project_config["backend_package"]}.repository.{entity_name}Repository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class {entity_name}Service {{
    @Autowired
    private {entity_name}Repository repository;

    public List<{entity_name}> findAll() {{
        return repository.findAll();
    }}

    public Optional<{entity_name}> findById(Long id) {{
        return repository.findById(id);
    }}

    public {entity_name} save({entity_name} {entity_name_lower}) {{
        return repository.save({entity_name_lower});
    }}

    public void delete(Long id) {{
        repository.deleteById(id);
    }}
}}
""")

    def _generate_controller(self, entity, src_path, entity_name, entity_name_lower):
        """Genera un controller REST per l'entità"""
        controller_path = os.path.join(src_path, "controller")
        os.makedirs(controller_path, exist_ok=True)

        with open(os.path.join(controller_path, f"{entity_name}Controller.java"), "w") as f:
            f.write(f"""
package {self.project_config["backend_package"]}.controller;

import {self.project_config["backend_package"]}.model.{entity_name};
import {self.project_config["backend_package"]}.service.{entity_name}Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/{entity_name_lower}")
public class {entity_name}Controller {{
    @Autowired
    private {entity_name}Service service;

    @GetMapping("/")
    public List<{entity_name}> getAll() {{
        return service.findAll();
    }}

    @GetMapping("/{id}")
    public Optional<{entity_name}> getById(@PathVariable Long id) {{
        return service.findById(id);
    }}

    @PostMapping("/")
    public {entity_name} create(@RequestBody {entity_name} {entity_name_lower}) {{
        return service.save({entity_name_lower});
    }}

    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {{
        service.delete(id);
    }}
}}
""")

    def _log(self, message):
        print(f"[BackendGenerator] {message}")
