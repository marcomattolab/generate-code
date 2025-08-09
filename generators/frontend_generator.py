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
        app_name = self.project_config["app"]
        run_cmd(
            f"npx -y @angular/cli@latest new {app_name} --style=scss --routing=false --skip-git --skip-install",
            cwd=frontend_dir,
        )

        app_path = os.path.join(frontend_dir, app_name)
        if not os.path.exists(app_path):
            raise FileNotFoundError("Angular project not found. Check if 'app' was created.")

        # 2. Install core dependencies
        self._install_dependencies(app_path)

        # 3. Generate UI based on entities.json
        self._generate_app_component(app_path)
        self._generate_components(app_path)

        # 4. Update app config and styles
        self._update_app_config(app_path)
        self._update_styles(app_path)

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

        form_controls = []
        for col in entity["columns"]:
            if col["name"].lower() == 'id':
                continue
            form_controls.append(f'"{col["name"]}": ["", [Validators.required]]')

        form_controls_str = ",\n    ".join(form_controls)

        primeng_imports = {
            "ButtonModule": "primeng/button",
            "InputTextModule": "primeng/inputtext",
        }

        if any(col.get("type") == "number" for col in entity["columns"] if col.get("name", "").lower() != "id"):
            primeng_imports["InputNumberModule"] = "primeng/inputnumber"

        import_statements = [f"import {{ {mod} }} from '{path}';" for mod, path in primeng_imports.items()]
        primeng_imports_str = "\n".join(import_statements)
        primeng_modules_str = ", ".join(primeng_imports.keys())

        return f"""import {{ Component, inject }} from '@angular/core';
import {{ FormBuilder, ReactiveFormsModule, Validators }} from '@angular/forms';
import {{ CommonModule }} from '@angular/common';
{primeng_imports_str}

@Component({{
  selector: 'app-{entity["name"].lower()}',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, {primeng_modules_str}],
  templateUrl: './{entity["name"].lower()}.component.html'
}})
export class {class_name}Component {{
  private fb = inject(FormBuilder);

  form = this.fb.group({{
    {form_controls_str}
  }});

  save(): void {{
    if (this.form.invalid) {{
      this.form.markAllAsTouched();
      return;
    }}
    console.log('Saving...', this.form.value);
    // Here you would typically call a service to save the data
  }}
}}
"""

    def _generate_component_html(self, entity):
        inputs = []
        for col in entity["columns"]:
            col_name = col["name"]
            col_type = col.get("type", "string")

            if col_name.lower() == 'id':
                continue

            input_html = ''
            if col_type == 'number':
                input_html = f'<p-inputNumber inputId="{col_name}" formControlName="{col_name}" mode="decimal" [showButtons]="true"></p-inputNumber>'
            else:
                input_html = f'<input id="{col_name}" type="text" pInputText formControlName="{col_name}" />'

            field_html = f"""<div class="field col-12">
        <label for="{col_name}" class="font-semibold">{col_name.capitalize()}</label>
        {input_html}
      </div>"""
            inputs.append(field_html)

        inputs_html = '\\n      '.join(inputs)

        return f"""<div class="card p-fluid">
  <h2 class="text-2xl font-bold mb-4">{entity["name"]} Form</h2>
  <form [formGroup]="form" (ngSubmit)="save()">
    <div class="formgrid grid">
      {inputs_html}
    </div>
    <div class="mt-4 flex justify-content-end">
        <p-button label="Save" type="submit" icon="pi pi-check" [disabled]="form.invalid"></p-button>
    </div>
  </form>
</div>
"""

    def _generate_entities_routes(self, entities):
        if not entities:
            return "import { Routes } from '@angular/router';\n\nexport const routes: Routes = [];"

        first_entity_path = entities[0]["name"].lower()

        routes = ",\n  ".join(
            f"""{{
      path: '{entity["name"].lower()}',
      loadComponent: () => import('./components/{entity["name"].lower()}/{entity["name"].lower()}.component').then(m => m.{entity["name"].capitalize()}Component)
    }}""" for entity in entities
        )

        return f"""import {{ Routes }} from '@angular/router';

export const routes: Routes = [
  {{
    path: '',
    redirectTo: '{first_entity_path}',
    pathMatch: 'full'
  }},
  {routes}
];
"""

    def _generate_app_component(self, path):
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]

        src_app_dir = os.path.join(path, "src", "app")
        os.makedirs(src_app_dir, exist_ok=True)

        # app.component.ts
        entity_list = ",\n    ".join([f"{{ name: '{e['name'].capitalize()}', path: '/{e['name'].lower()}' }}" for e in entities])
        ts_code = f'''import {{ Component }} from '@angular/core';
import {{ RouterModule }} from '@angular/router';
import {{ CommonModule }} from '@angular/common';

@Component({{
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
}})
export class AppComponent {{
  entities = [
    {entity_list}
  ];
}}
'''
        with open(os.path.join(src_app_dir, "app.component.ts"), "w") as f:
            f.write(ts_code)

        # app.component.html
        html_code = f'''<div class="flex h-screen bg-gray-100 font-sans">
  <!-- Sidebar -->
  <div class="w-64 bg-gray-800 text-white p-5 flex flex-col shadow-lg">
    <div class="text-2xl font-bold mb-10 text-center">
      <a routerLink="/" class="text-white no-underline">App</a>
    </div>
    <nav>
      <ul class="space-y-2">
        <li *ngFor="let entity of entities">
          <a [routerLink]="entity.path" routerLinkActive="active-link" class="flex items-center p-2 text-base font-normal text-gray-200 rounded-lg hover:bg-gray-700 transition-colors duration-200">
            <span class="ml-3">{{{{ entity.name }}}}</span>
          </a>
        </li>
      </ul>
    </nav>
  </div>

  <!-- Main Content -->
  <main class="flex-1 p-10 overflow-y-auto">
    <div class="bg-white p-8 rounded-lg shadow-md">
      <router-outlet></router-outlet>
    </div>
  </main>
</div>
'''
        with open(os.path.join(src_app_dir, "app.component.html"), "w") as f:
            f.write(html_code)

        # app.component.scss
        scss_code = '''
.active-link {
  background-color: #4f46e5; /* indigo-600 */
  color: white;
}
'''
        with open(os.path.join(src_app_dir, "app.component.scss"), "w") as f:
            f.write(scss_code)

    def _update_app_config(self, app_path):
        app_config_path = os.path.join(app_path, "src", "app", "app.config.ts")

        with open(app_config_path, "r") as f:
            content = f.read()

        # Add imports for router and animations
        imports_to_add = """import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideAnimations } from '@angular/platform-browser/animations';
"""

        # Prepend the imports to be safe
        content = imports_to_add + content

        # Add providers for routing and animations
        if "providers: [" in content:
            content = content.replace(
                "providers: [",
                "providers: [provideRouter(routes), provideAnimations(),"
            )
        else:
            # This case is unlikely with modern Angular CLI, but as a fallback
            content = content.replace(
                "providers: []",
                "providers: [provideRouter(routes), provideAnimations()]"
            )

        with open(app_config_path, "w") as f:
            f.write(content)

    def _update_styles(self, app_path):
        styles_path = os.path.join(app_path, "src", "styles.scss")

        styles_to_add = """
@import "primeng/resources/themes/lara-light-blue/theme.css";
@import "primeng/resources/primeng.css";
@import "primeicons/primeicons.css";
@import "primeflex/primeflex.css";
"""

        with open(styles_path, "a") as f:
            f.write(styles_to_add)
