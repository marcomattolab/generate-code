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

        # Step 1: Create Spring Boot base structure and configuration
        self._create_basic_structure(backend_path)
        self._generate_application_properties(backend_path)

        # Step 2: Generate entities, repositories, services, and controllers
        self._generate_entities_and_services(backend_path)

    def _create_basic_structure(self, path):
        """Downloads and unzips the base Spring Boot project."""
        self._log("Creating Spring Boot base structure...")
        run_cmd("curl https://start.spring.io/starter.zip -d dependencies=web,data-jpa,postgresql,lombok -o app.zip", cwd=path)
        run_cmd("unzip app.zip -d .", cwd=path)
        os.remove(os.path.join(path, "app.zip"))

    def _generate_application_properties(self, path):
        """Generates the application.properties file for PostgreSQL configuration."""
        properties_path = os.path.join(path, "src", "main", "resources", "application.properties")

        properties_content = """spring.datasource.url=jdbc:postgresql://localhost:5432/mydatabase
spring.datasource.username=myuser
spring.datasource.password=mypassword
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
"""

        with open(properties_path, "w") as f:
            f.write(properties_content)

    def _generate_entities_and_services(self, path):
        """Genera entità JPA, repository, controller, e service da entities.json"""
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]

        src_path = os.path.join(path, "src", "main", "java", *self.project_config["backend_package"].split("."))
        os.makedirs(src_path, exist_ok=True)

        for entity in entities:
            entity_name = entity["name"]
            entity_name_lower = entity_name.lower()

            # Generate Entity, DTO, and Mapper
            self._generate_entity(entity, src_path, entity_name, entity_name_lower)
            self._generate_dto(entity, src_path, entity_name)
            self._generate_mapper(entity, src_path, entity_name)

            # Generate Repository
            self._generate_repository(entity, src_path, entity_name, entity_name_lower)

            # Creazione Service
            self._generate_service(entity, src_path, entity_name, entity_name_lower)

            # Creazione Controller
            self._generate_controller(entity, src_path, entity_name, entity_name_lower)

    def _generate_entity(self, entity, src_path, entity_name, entity_name_lower):
        """Generates a JPA Entity class for the given entity."""
        entity_path = os.path.join(src_path, "model")
        os.makedirs(entity_path, exist_ok=True)

        entity_fields = []
        for col in entity["columns"]:
            if col['name'].lower() == 'id':
                continue
            java_type = self._map_type(col['type'])
            entity_fields.append(f"    private {java_type} {col['name']};")

        entity_fields_str = "\n".join(entity_fields)

        with open(os.path.join(entity_path, f"{entity_name}.java"), "w") as f:
            f.write(f"""
package {self.project_config["backend_package"]}.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "{entity_name_lower}s")
public class {entity_name} {{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

{entity_fields_str}
}}
""")

    def _generate_dto(self, entity, src_path, entity_name):
        """Generates a DTO class for the given entity."""
        dto_path = os.path.join(src_path, "dto")
        os.makedirs(dto_path, exist_ok=True)

        dto_fields = []
        for col in entity["columns"]:
            java_type = self._map_type(col['type'])
            dto_fields.append(f"    private {java_type} {col['name']};")

        dto_fields_str = "\n".join(dto_fields)

        with open(os.path.join(dto_path, f"{entity_name}Dto.java"), "w") as f:
            f.write(f'''
package {self.project_config["backend_package"]}.dto;

import lombok.Data;

@Data
public class {entity_name}Dto {{
{dto_fields_str}
}}
''')

    def _generate_mapper(self, entity, src_path, entity_name):
        """Generates a Mapper class for the given entity and its DTO."""
        mapper_path = os.path.join(src_path, "mapper")
        os.makedirs(mapper_path, exist_ok=True)

        package_name = self.project_config["backend_package"]

        to_dto_mappings = []
        to_entity_mappings = []
        for col in entity["columns"]:
            col_name = col["name"]
            cap_col_name = col_name[0].upper() + col_name[1:]
            to_dto_mappings.append(f"        dto.set{cap_col_name}(entity.get{cap_col_name}());")
            to_entity_mappings.append(f"        entity.set{cap_col_name}(dto.get{cap_col_name}());")

        to_dto_mappings_str = "\n".join(to_dto_mappings)
        to_entity_mappings_str = "\n".join(to_entity_mappings)

        with open(os.path.join(mapper_path, f"{entity_name}Mapper.java"), "w") as f:
            f.write(f'''
package {package_name}.mapper;

import {package_name}.dto.{entity_name}Dto;
import {package_name}.model.{entity_name};

public class {entity_name}Mapper {{

    public static {entity_name}Dto toDto({entity_name} entity) {{
        if (entity == null) {{
            return null;
        }}

        {entity_name}Dto dto = new {entity_name}Dto();
{to_dto_mappings_str}
        return dto;
    }}

    public static {entity_name} toEntity({entity_name}Dto dto) {{
        if (dto == null) {{
            return null;
        }}

        {entity_name} entity = new {entity_name}();
{to_entity_mappings_str}
        return entity;
    }}
}}
''')

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
        """Generates a service class for the entity."""
        service_path = os.path.join(src_path, "service")
        os.makedirs(service_path, exist_ok=True)

        package_name = self.project_config["backend_package"]
        mapper_name = f"{entity_name}Mapper"

        with open(os.path.join(service_path, f"{entity_name}Service.java"), "w") as f:
            f.write(f'''
package {package_name}.service;

import {package_name}.dto.{entity_name}Dto;
import {package_name}.model.{entity_name};
import {package_name}.repository.{entity_name}Repository;
import {package_name}.mapper.{mapper_name};
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class {entity_name}Service {{
    @Autowired
    private {entity_name}Repository repository;

    public List<{entity_name}Dto> findAll() {{
        return repository.findAll().stream()
                .map({mapper_name}::toDto)
                .collect(Collectors.toList());
    }}

    public Optional<{entity_name}Dto> findById(Long id) {{
        return repository.findById(id)
                .map({mapper_name}::toDto);
    }}

    public {entity_name}Dto save({entity_name}Dto {entity_name_lower}Dto) {{
        {entity_name} entity = {mapper_name}.toEntity({entity_name_lower}Dto);
        entity = repository.save(entity);
        return {mapper_name}.toDto(entity);
    }}

    public void delete(Long id) {{
        repository.deleteById(id);
    }}
}}
''')

    def _generate_controller(self, entity, src_path, entity_name, entity_name_lower):
        """Generates a REST controller for the entity."""
        controller_path = os.path.join(src_path, "controller")
        os.makedirs(controller_path, exist_ok=True)

        package_name = self.project_config["backend_package"]
        dto_name = f"{entity_name}Dto"

        with open(os.path.join(controller_path, f"{entity_name}Controller.java"), "w") as f:
            f.write(f'''
package {package_name}.controller;

import {package_name}.dto.{dto_name};
import {package_name}.service.{entity_name}Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/{entity_name_lower}s")
public class {entity_name}Controller {{
    @Autowired
    private {entity_name}Service service;

    @GetMapping
    public List<{dto_name}> getAll() {{
        return service.findAll();
    }}

    @GetMapping("/{{id}}")
    public ResponseEntity<{dto_name}> getById(@PathVariable Long id) {{
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }}

    @PostMapping
    public {dto_name} create(@RequestBody {dto_name} dto) {{
        return service.save(dto);
    }}

    @PutMapping("/{{id}}")
    public ResponseEntity<{dto_name}> update(@PathVariable Long id, @RequestBody {dto_name} dto) {{
        dto.setId(id);
        return ResponseEntity.ok(service.save(dto));
    }}

    @DeleteMapping("/{{id}}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {{
        service.delete(id);
        return ResponseEntity.noContent().build();
    }}
}}
''')

    def _map_type(self, column_type):
        if column_type == 'string':
            return 'String'
        elif column_type == 'number':
            return 'Long'
        else:
            return 'String'

    def _log(self, message):
        print(f"[BackendGenerator] {message}")
