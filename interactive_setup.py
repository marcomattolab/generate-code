import json
import questionary

def main():
    print("🚀 Welcome to the Full-Stack App Generator Interactive Setup! 🚀")
    print("I'll guide you through creating your project configuration.")

    # --- Project Setup ---
    print("\n--- Project Configuration ---")
    project_name = questionary.text("Enter the root directory name for your generated project:", default="generated_app").ask()
    frontend_app = questionary.text("Enter the name for your Angular app:", default="app").ask()
    backend_package = questionary.text("Enter the Java package name for your backend:", default="com.example.backend").ask()
    mobile_app = questionary.text("Enter the name for your Flutter mobile app:", default="my_flutter_app").ask()

    features = {
        "authentication": questionary.confirm("Enable Keycloak authentication?").ask(),
        "monitoring": questionary.confirm("Enable Prometheus & Grafana monitoring?").ask()
    }

    project_config = {
        "project": {
            "name": project_name,
            "app": frontend_app,
            "backend": "backend",
            "frontend": "frontend",
            "backend_package": backend_package,
            "mobile_app": mobile_app,
            "features": features
        }
    }

    # --- Entities Setup ---
    print("\n--- Entity Configuration ---")
    entities = []
    add_another_entity = True
    while add_another_entity:
        entity_name = questionary.text("Enter the name for a new entity (e.g., User, Product):").ask()

        columns = []
        add_another_column = True
        while add_another_column:
            col_name = questionary.text(f"Enter a column name for {entity_name}:").ask()
            col_type = questionary.select(
                f"Select the type for the '{col_name}' column:",
                choices=["string", "number"]
            ).ask()
            columns.append({"name": col_name, "type": col_type})
            add_another_column = questionary.confirm("Add another column to this entity?").ask()

        entity = {"name": entity_name, "columns": columns}

        if questionary.confirm("Add relationships to this entity?").ask():
            relationships = []
            add_another_relationship = True
            while add_another_relationship:
                rel_type = questionary.select(
                    "Select the relationship type:",
                    choices=["manyToOne", "oneToMany"]
                ).ask()
                rel_entity = questionary.text("Enter the name of the other entity in the relationship:").ask()
                rel_name = questionary.text("Enter the name for this relationship field:").ask()

                rel_data = {"type": rel_type, "entity": rel_entity, "name": rel_name}

                if rel_type == "oneToMany":
                    mapped_by = questionary.text("Enter the 'mappedBy' value (the field on the other entity):").ask()
                    rel_data["mappedBy"] = mapped_by

                relationships.append(rel_data)
                add_another_relationship = questionary.confirm("Add another relationship to this entity?").ask()
            entity["relationships"] = relationships

        entities.append(entity)
        add_another_entity = questionary.confirm("Add another entity?").ask()

    entities_config = {"entities": entities}

    # --- Final Confirmation ---
    print("\n--- Generated Configuration ---")
    print("\nproject.json:")
    print(json.dumps(project_config, indent=2))
    print("\nentities.json:")
    print(json.dumps(entities_config, indent=2))

    if questionary.confirm("Do you want to save this configuration?").ask():
        with open("project.json", "w") as f:
            json.dump(project_config, f, indent=2)
        with open("entities.json", "w") as f:
            json.dump(entities_config, f, indent=2)
        print("\n✅ Configuration saved successfully!")
    else:
        print("\n❌ Setup cancelled.")

if __name__ == "__main__":
    main()
