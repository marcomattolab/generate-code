import os
import json
from utils import run_cmd

class FrontendGenerator:
    def __init__(self, root_dir, entities_file, project_config):
        self.root_dir = root_dir
        self.entities_file = entities_file
        self.project_config = project_config

    def generate(self):
        frontend_dir = os.path.join(self.root_dir, self.project_config["frontend"])
        os.makedirs(frontend_dir, exist_ok=True)

        # 1. Generate Angular App
        run_cmd("npx -y @angular/cli@latest new app --style=scss --routing=true --skip-git --skip-install ", cwd=frontend_dir)

        app_path = os.path.join(frontend_dir, "app")
        if not os.path.exists(app_path):
            raise FileNotFoundError("Angular project not found. Check if 'app' was created.")

        # 2. Install core dependencies
        self._install_dependencies(app_path)

        # 3. Generate UI based on entities.json
        self._generate_components(app_path)


    def _install_dependencies(self, path):
        deps = [
            "primeng", "primeicons", "primeflex",
            "@angular/animations",
            "@angular/forms"
        ]
        run_cmd(f"npm install {' '.join(deps)}", cwd=path)

        dev_deps = [
        "@storybook/angular", "@storybook/cli",
        "@angular-eslint/schematics"
        ]
        run_cmd(f"npm install --save-dev {' '.join(dev_deps)}", cwd=path)

        # run_cmd("npx -y sb init --builder webpack5", cwd=path)


    def _generate_components(self, path):
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]

        components_dir = os.path.join(path, "src", "app", "components")
        os.makedirs(components_dir, exist_ok=True)

        for entity in entities:
            name = entity["name"].lower()
            class_name = entity["name"].capitalize()
            entity_path = os.path.join(components_dir, name)
            os.makedirs(entity_path, exist_ok=True)

            # .component.ts
            with open(os.path.join(entity_path, f"{name}.component.ts"), "w") as f:
                f.write(self._generate_component_code(entity))
            # .component.html
            with open(os.path.join(entity_path, f"{name}.component.html"), "w") as f:
                f.write(self._generate_component_html(entity))
            # Optional: routing + service + test generation here


    def _generate_component_code(self, entity):
        return f"""
import {{ Component, OnInit }} from '@angular/core';

@Component({{
  selector: 'app-{entity["name"].lower()}',
  templateUrl: './{entity["name"].lower()}.component.html'
}})
export class {entity["name"]}Component implements OnInit {{
  constructor() {{ }}
  ngOnInit(): void {{ }}
}}
"""

    def _generate_component_html(self, entity):
        inputs = "\n".join(
            f"""<div class="field">
  <label for="{col['name']}">{col['name'].capitalize()}</label>
  <input id="{col['name']}" type="text" pInputText />
</div>"""
            for col in entity["columns"]
        )

        return f"""<div class="card">
  <h2 class="text-xl mb-3">{entity["name"]} Form</h2>
  <form>
    {inputs}
    <button pButton type="button" label="Save" class="mt-3"></button>
  </form>
</div>
"""
