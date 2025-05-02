import os
import json
from utils import run_cmd

class FrontendGenerator:
    def __init__(self, root_dir, entities_file, project_config):
        self.root_dir = root_dir
        self.entities_file = entities_file
        self.project_config = project_config

    def generate(self):

        frontend_path = os.path.join(self.root_dir, self.project_config["frontend"])
        os.makedirs(frontend_path, exist_ok=True)

        app_path = os.path.join(frontend_path, "app")
        os.makedirs(app_path, exist_ok=True)

        run_cmd("npx -y @angular/cli@latest new app --style=scss --routing=true --skip-git --skip-install", cwd=frontend_path)
        self._install_dependencies(os.path.join(frontend_path, "app"))
        # self._generate_components(os.path.join(frontend_path, "app"))

    def _install_dependencies(self, path):
        run_cmd("npm install primeng primeicons", cwd=path)
        #run_cmd("npm install cypress --save-dev", cwd=path)
        #run_cmd("npx cypress open", cwd=path)
        #run_cmd("npx -y sb init --builder webpack5", cwd=path)
        #run_cmd("ng add @angular-eslint/schematics", cwd=path)


    def _generate_components(self, path):
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]
        for entity in entities:
            component_dir = os.path.join(path, "src", "app", "components", entity["name"].lower())
            os.makedirs(component_dir, exist_ok=True)
            with open(os.path.join(component_dir, f"{entity['name'].lower()}.component.ts"), "w") as f:
                f.write(self._generate_component_code(entity))
            with open(os.path.join(component_dir, f"{entity['name'].lower()}.component.html"), "w") as f:
                f.write(self._generate_component_html(entity))

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
        return f"""
<h2>{entity["name"]} Component with PrimeNG</h2>
<p-inputText placeholder="Enter {entity["name"]} info"></p-inputText>
"""
