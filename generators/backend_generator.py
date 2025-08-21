import os
import json
from utils import run_cmd

class BackendGenerator:
    def __init__(self, root_dir, entities_file, project_config):
        self.root_dir = root_dir
        self.entities_file = entities_file
        self.project_config = project_config
        self.backend_path = os.path.join(self.root_dir, self.project_config["backend"])
        self.src_path = os.path.join(self.backend_path, "src", "main", "java", *self.project_config["backend_package"].split("."))

    def generate(self):
        os.makedirs(self.backend_path, exist_ok=True)

        # Step 1: Create Spring Boot base structure and configuration
        self._create_manual_structure()
        self._generate_application_properties()
        self._create_main_application_file()

        # Step 2: Generate entities, repositories, services, and controllers
        self._generate_entities_and_services()

    def _create_manual_structure(self):
        """Creates the base Spring Boot project structure manually."""
        print("Creating Spring Boot base structure manually...")

        # Create standard Maven directories
        os.makedirs(os.path.join(self.backend_path, "src", "main", "resources"), exist_ok=True)
        os.makedirs(os.path.join(self.backend_path, "src", "test", "java"), exist_ok=True)
        os.makedirs(self.src_path, exist_ok=True)

        # Create pom.xml
        pom_content = self._get_pom_xml_content()
        with open(os.path.join(self.backend_path, "pom.xml"), "w") as f:
            f.write(pom_content)

    def _get_pom_xml_content(self):
        group_id = self.project_config["backend_package"]
        artifact_id = self.project_config["backend"]
        name = self.project_config["name"]
        description = self.project_config.get("description", "Demo project for Spring Boot")

        dependencies = [
            "<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>",
            "<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>",
            "<dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>runtime</scope></dependency>",
            "<dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>",
            "<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>"
        ]

        if self.project_config.get("features", {}).get("authentication"):
            dependencies.append("<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-oauth2-resource-server</artifactId></dependency>")
        if self.project_config.get("features", {}).get("monitoring"):
            dependencies.append("<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>")
            dependencies.append("<dependency><groupId>io.micrometer</groupId><artifactId>micrometer-registry-prometheus</artifactId></dependency>")

        dependencies_str = "\n        ".join(dependencies)

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.5</version>
        <relativePath/>
    </parent>
    <groupId>{group_id}</groupId>
    <artifactId>{artifact_id}</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>{name}</name>
    <description>{description}</description>
    <properties>
        <java.version>17</java.version>
    </properties>
    <dependencies>
        {dependencies_str}
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
'''

    def _create_main_application_file(self):
        """Creates the main Spring Boot application class."""
        package_name = self.project_config["backend_package"]
        app_name = "".join(word.capitalize() for word in self.project_config["name"].split("-")) + "Application"

        main_app_content = f"""
package {package_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class {app_name} {{

    public static void main(String[] args) {{
        SpringApplication.run({app_name}.class, args);
    }}

}}
"""
        with open(os.path.join(self.src_path, f"{app_name}.java"), "w") as f:
            f.write(main_app_content)


    def _generate_application_properties(self):
        """Generates the application.properties file for PostgreSQL configuration."""
        properties_path = os.path.join(self.backend_path, "src", "main", "resources", "application.properties")

        properties_content = """spring.datasource.url=jdbc:postgresql://localhost:5432/mydatabase
spring.datasource.username=myuser
spring.datasource.password=mypassword
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
"""

        if self.project_config.get("features", {}).get("monitoring"):
            properties_content += "management.endpoints.web.exposure.include=prometheus\n"

        if self.project_config.get("features", {}).get("authentication"):
            properties_content += "\n# Keycloak\n"
            properties_content += "spring.security.oauth2.resourceserver.jwt.issuer-uri=http://localhost:8081/realms/myrealm\n"

        with open(properties_path, "w") as f:
            f.write(properties_content)

    def _generate_entities_and_services(self):
        """Genera entità JPA, repository, controller, e service da entities.json"""
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]

        for entity in entities:
            entity_name = entity["name"]
            entity_name_lower = entity_name.lower()

            self._generate_entity(entity, self.src_path, entity_name, entity_name_lower)
            self._generate_dto(entity, self.src_path, entity_name)
            self._generate_mapper(entity, self.src_path, entity_name)
            self._generate_repository(entity, self.src_path, entity_name, entity_name_lower)
            self._generate_service(entity, self.src_path, entity_name, entity_name_lower)
            self._generate_controller(entity, self.src_path, entity_name, entity_name_lower)

        self._generate_dashboard_service(self.src_path, entities)
        self._generate_dashboard_controller(self.src_path)

        if self.project_config.get("features", {}).get("authentication"):
            self._generate_security_config(self.src_path)

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

        if "relationships" in entity:
            for rel in entity["relationships"]:
                if rel["type"] == "manyToOne":
                    rel_entity = rel["entity"]
                    rel_name = rel["name"]
                    entity_fields.append(f'\n    @ManyToOne\n    @JoinColumn(name = "{rel_name}_id")\n    private {rel_entity} {rel_name};')
                elif rel["type"] == "oneToMany":
                    rel_entity = rel["entity"]
                    rel_name = rel["name"]
                    mapped_by = rel["mappedBy"]
                    entity_fields.append(f'\n    @OneToMany(mappedBy = "{mapped_by}")\n    private java.util.List<{rel_entity}> {rel_name};')


        entity_fields_str = "\n".join(entity_fields)

        with open(os.path.join(entity_path, f"{entity_name}.java"), "w") as f:
            f.write(f'''
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
''')

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
            f.write(f'''
package {self.project_config["backend_package"]}.repository;

import {self.project_config["backend_package"]}.model.{entity_name};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface {entity_name}Repository extends JpaRepository<{entity_name}, Long> {{
}}
''')

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

        authentication_enabled = self.project_config.get("features", {}).get("authentication")

        imports = [
            f'import {package_name}.dto.{dto_name};',
            f'import {package_name}.service.{entity_name}Service;',
            'import org.springframework.beans.factory.annotation.Autowired;',
            'import org.springframework.http.ResponseEntity;',
            'import org.springframework.web.bind.annotation.*;',
            'import java.util.List;'
        ]

        annotations = [
            '@RestController',
            f'@RequestMapping("/api/{entity_name_lower}s")'
        ]

        if authentication_enabled:
            imports.append('import org.springframework.security.access.prepost.PreAuthorize;')
            annotations.append('@PreAuthorize("hasRole(\'user\')")')

        imports_str = "\n".join(imports)
        annotations_str = "\n".join(annotations)

        with open(os.path.join(controller_path, f"{entity_name}Controller.java"), "w") as f:
            f.write(f'''
package {package_name}.controller;

{imports_str}

{annotations_str}
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

    def _generate_security_config(self, src_path):
        """Generates a SecurityConfig class."""
        config_path = os.path.join(src_path, "config")
        os.makedirs(config_path, exist_ok=True)

        security_config_content = f'''
package {self.project_config["backend_package"]}.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {{

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {{
        http
            .authorizeHttpRequests(authorize -> authorize
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt());
        return http.build();
    }}
}}
'''

        with open(os.path.join(config_path, "SecurityConfig.java"), "w") as f:
            f.write(security_config_content)

    def _generate_dashboard_service(self, src_path, entities):
        """Generates a DashboardService class."""
        service_path = os.path.join(src_path, "service")
        os.makedirs(service_path, exist_ok=True)

        repo_imports = "\n".join([f"import {self.project_config['backend_package']}.repository.{entity['name']}Repository;" for entity in entities])
        repo_injections = "\n    ".join([f"@Autowired\n    private {entity['name']}Repository {entity['name'].lower()}Repository;" for entity in entities])

        counts = ",\n            ".join([f'"{entity["name"].lower()}s", {entity["name"].lower()}Repository.count()' for entity in entities])

        service_content = f'''
package {self.project_config["backend_package"]}.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.Map;
import java.util.HashMap;
{repo_imports}

@Service
public class DashboardService {{
    {repo_injections}

    public Map<String, Long> getEntityCounts() {{
        Map<String, Long> counts = new HashMap<>();
        counts.putAll(Map.of(
            {counts}
        ));
        return counts;
    }}
}}
'''

        with open(os.path.join(service_path, "DashboardService.java"), "w") as f:
            f.write(service_content)

    def _generate_dashboard_controller(self, src_path):
        """Generates a DashboardController class."""
        controller_path = os.path.join(src_path, "controller")
        os.makedirs(controller_path, exist_ok=True)

        controller_content = f'''
package {self.project_config["backend_package"]}.controller;

import {self.project_config["backend_package"]}.service.DashboardService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/dashboard")
@PreAuthorize("hasRole('admin')")
public class DashboardController {{
    @Autowired
    private DashboardService service;

    @GetMapping("/counts")
    public Map<String, Long> getEntityCounts() {{
        return service.getEntityCounts();
    }}
}}
'''

        with open(os.path.join(controller_path, "DashboardController.java"), "w") as f:
            f.write(controller_content)

    def _map_type(self, column_type):
        if column_type == 'string':
            return 'String'
        elif column_type == 'number':
            return 'Long'
        else:
            return 'String'

    def _log(self, message):
        print(f"[BackendGenerator] {message}")
