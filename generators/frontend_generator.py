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
        run_cmd(
            "npx -y @angular/cli@latest new app --style=scss --routing=false --skip-git --skip-install",
            cwd=frontend_dir,
        )

        app_path = os.path.join(frontend_dir, "app")
        if not os.path.exists(app_path):
            raise FileNotFoundError("Angular project not found. Check if 'app' was created.")

        # 2. Install core dependencies
        self._install_dependencies(app_path)

        # 3. Generate UI based on entities.json
        self._generate_components(app_path)
        self._generate_app_component(app_path)

    def _install_dependencies(self, path):
        deps = [
            "primeng", "primeicons", "primeflex",
            "@angular/animations",
            "@angular/forms"
        ]
        run_cmd(f"npm install {' '.join(deps)}", cwd=path)

        dev_deps = [
            "@storybook/angular", "@storybook/cli",
            "@angular-eslint/schematics",
            "prettier"
        ]
        run_cmd(f"npm install --save-dev {' '.join(dev_deps)}", cwd=path)

    def _generate_components(self, path):
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]

        components_dir = os.path.join(path, "src", "app", "components")
        os.makedirs(components_dir, exist_ok=True)

        for entity in entities:
            name = entity["name"].lower()
            entity_path = os.path.join(components_dir, name)
            os.makedirs(entity_path, exist_ok=True)

            # .component.ts
            with open(os.path.join(entity_path, f"{name}.component.ts"), "w") as f:
                f.write(self._generate_component_code(entity))

            # .component.html
            with open(os.path.join(entity_path, f"{name}.component.html"), "w") as f:
                f.write(self._generate_component_html(entity))

        # Generate app.routes.ts
        routes_file_path = os.path.join(path, "src", "app", "app.routes.ts")
        with open(routes_file_path, "w") as f:
            f.write(self._generate_entities_routes(entities))

    def _generate_component_code(self, entity):
        class_name = entity["name"].capitalize()
        form_controls = ",\n    ".join(
            f'"{col["name"]}": [""]' for col in entity["columns"]
        )

        return f"""import {{ Component, signal, inject }} from '@angular/core';
import {{ FormBuilder, ReactiveFormsModule }} from '@angular/forms';
import {{ CommonModule }} from '@angular/common';
import {{ InputTextModule }} from 'primeng/inputtext';
import {{ ButtonModule }} from 'primeng/button';

@Component({{
  selector: 'app-{entity["name"].lower()}',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, InputTextModule, ButtonModule],
  templateUrl: './{entity["name"].lower()}.component.html'
}})
export class {class_name}Component {{

  private fb = inject(FormBuilder);
  form = this.fb.group({{
    {form_controls}
  }});

  submit = signal(false);

  save() {{
    this.submit.set(true);
    console.log("Saving", this.form.value);
  }}
}}
"""

    def _generate_component_html(self, entity):
        inputs = "\n    ".join(
            f"""<div class="field mb-3">
      <label for="{col['name']}" class="block text-sm font-medium text-gray-700">{col['name'].capitalize()}</label>
      <input id="{col['name']}" type="text" pInputText formControlName="{col['name']}" class="w-full" />
    </div>""" for col in entity["columns"]
        )

        return f"""<div class="card p-4 shadow-lg rounded bg-white">
  <h2 class="text-2xl font-semibold mb-4">{entity["name"]} Form</h2>
  <form [formGroup]="form" (ngSubmit)="save()">
    {inputs}
    <button pButton type="submit" label="Save" class="mt-4"></button>
  </form>
</div>
"""

    def _generate_entities_routes(self, entities):
        routes = ",\n  ".join(
            f"""{{
  path: '{entity["name"].lower()}',
  loadComponent: () => import('./components/{entity["name"].lower()}/{entity["name"].lower()}.component').then(m => m.{entity["name"]}Component)
}}""" for entity in entities
        )

        return f"""import {{ Routes }} from '@angular/router';
import {{ AppComponent }} from './app.component';

export const routes: Routes = [
  {{
    path: '',
    component: AppComponent
  }},
  {routes}
];
"""

    def _generate_app_component(self, path):
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]

        src_app_dir = os.path.join(path, "src", "app")
        os.makedirs(src_app_dir, exist_ok=True)

        entity_array = ",\n    ".join(
            f"{{ name: '{entity['name']}' }}" for entity in entities
        )

        # TypeScript
        with open(os.path.join(src_app_dir, "app.component.ts"), "w") as f:
            f.write(f"""import {{ Component, signal, inject }} from '@angular/core';
import {{ RouterModule, Router }} from '@angular/router';
import {{ CommonModule }} from '@angular/common';
import {{ TableModule }} from 'primeng/table';
import {{ ButtonModule }} from 'primeng/button';

@Component({{
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule, TableModule, ButtonModule],
  templateUrl: './app.component.html'
}})
export class AppComponent {{
  private router = inject(Router);

  entities = signal([
    {entity_array}
  ]);

  goTo(path: string, action: 'view' | 'edit') {{
    this.router.navigate([path], {{ queryParams: {{ mode: action }} }});
  }}
}}
""")

        # HTML
        with open(os.path.join(src_app_dir, "app.component.html"), "w") as f:
            f.write("""<div class="p-4">
  <h1 class="text-2xl font-bold mb-4">Available Entities</h1>
  <p-table [value]="entities()">
    <ng-template pTemplate="header">
      <tr>
        <th>Name</th>
        <th style="width: 200px;">Actions</th>
      </tr>
    </ng-template>
    <ng-template pTemplate="body" let-entity>
      <tr>
        <td>{{ entity.name }}</td>
        <td>
          <button pButton label="View" class="p-button-sm mr-2" (click)="goTo(entity.name.toLowerCase(), 'view')"></button>
          <button pButton label="Edit" class="p-button-sm p-button-secondary" (click)="goTo(entity.name.toLowerCase(), 'edit')"></button>
        </td>
      </tr>
    </ng-template>
  </p-table>
</div>
""")
