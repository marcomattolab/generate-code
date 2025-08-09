import os
import json
from utils import run_cmd

class FrontendGenerator:
    def __init__(self, root_dir, entities_file, project_config):
        self.root_dir = root_dir
        self.entities_file = entities_file
        self.project_config = project_config

    def _log(self, message):
        print(f"[FrontendGenerator] {message}")

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

        # 5. Set up Storybook (temporarily disabled due to timeout)
        # self._setup_storybook(app_path)

        # 6. Set up Cypress
        self._setup_cypress(app_path)

        # 7. Configure Angular proxy
        self._create_proxy_config(app_path)
        self._update_angular_json_for_proxy(app_path)

        # 8. Generate i18n files
        self._generate_translation_files(app_path)

    def _install_dependencies(self, path):
        deps = [
            "primeng", "primeicons", "primeflex",
            "@angular/animations",
            "@angular/forms",
            "@ngx-translate/core",
            "@ngx-translate/http-loader"
        ]
        run_cmd(f"npm install {' '.join(deps)}", cwd=path)

        dev_deps = [
            "@storybook/angular", "@storybook/cli",
            "@angular-eslint/schematics",
            "prettier",
            "cypress"
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

            # .stories.ts
            self._generate_story(entity, entity_path, entity['name'])

            # .spec.ts
            self._generate_component_spec(entity, entity_path, entity['name'])

            # DTO and Service
            self._generate_frontend_dto(entity, path, entity['name'])
            self._generate_service(entity, path, entity['name'])

            # E2E spec
            self._generate_e2e_spec(entity, path, entity['name'])

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

        service_name = f"{class_name}Service"
        service_import = f"import {{ {service_name} }} from '../../core/services/{entity['name'].lower()}.service';"

        return f"""import {{ Component, inject }} from '@angular/core';
import {{ FormBuilder, ReactiveFormsModule, Validators }} from '@angular/forms';
import {{ CommonModule }} from '@angular/common';
{primeng_imports_str}
{service_import}

@Component({{
  selector: 'app-{entity["name"].lower()}',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, {primeng_modules_str}],
  templateUrl: './{entity["name"].lower()}.component.html'
}})
export class {class_name}Component {{
  private fb = inject(FormBuilder);
  private {entity['name'].lower()}Service = inject({service_name});

  form = this.fb.group({{
    {form_controls_str}
  }});

  save(): void {{
    if (this.form.invalid) {{
      this.form.markAllAsTouched();
      return;
    }}

    this.{entity['name'].lower()}Service.create(this.form.value as any).subscribe(() => {{
      console.log('Saved successfully!');
      // Optionally, reset the form or navigate away
      this.form.reset();
    }});
  }}
}}
"""

    def _generate_component_html(self, entity):
        inputs = []
        entity_name_upper = entity['name'].upper()
        for col in entity["columns"]:
            col_name = col["name"]
            col_type = col.get("type", "string")
            col_name_upper = col['name'].upper()

            if col_name.lower() == 'id':
                continue

            input_html = ''
            if col_type == 'number':
                input_html = f'<p-inputNumber inputId="{col_name}" formControlName="{col_name}" mode="decimal" [showButtons]="true"></p-inputNumber>'
            else:
                input_html = f'<input id="{col_name}" type="text" pInputText formControlName="{col_name}" />'

            field_html = f"""<div class="field col-12">
        <label for="{col_name}" class="font-semibold">{{{{ 'FIELD_{col_name_upper}' | translate }}}}</label>
        {input_html}
      </div>"""
            inputs.append(field_html)

        inputs_html = '\\n      '.join(inputs)

        return f"""<div class="card p-fluid">
  <h2 class="text-2xl font-bold mb-4">{{{{ '{entity_name_upper}_FORM_TITLE' | translate }}}}</h2>
  <form [formGroup]="form" (ngSubmit)="save()">
    <div class="formgrid grid">
      {inputs_html}
    </div>
    <div class="mt-4 flex justify-content-end">
        <p-button label="{{{{ 'SAVE_BUTTON' | translate }}}}" type="submit" icon="pi pi-check" [disabled]="form.invalid"></p-button>
    </div>
  </form>
</div>
"""

    def _generate_story(self, entity, component_path, entity_name):
        """Generates a Storybook story for a component."""
        story_path = os.path.join(component_path, f"{entity_name.lower()}.stories.ts")

        story_content = f"""
import type {{ Meta, StoryObj }} from '@storybook/angular';
import {{ {entity_name.capitalize()}Component }} from './{entity_name.lower()}.component';

const meta: Meta<{entity_name.capitalize()}Component> = {{
  title: 'Components/{entity_name.capitalize()}',
  component: {entity_name.capitalize()}Component,
  tags: ['autodocs'],
  render: (args: {entity_name.capitalize()}Component) => ({{
    props: {{
      ...args,
    }},
  }}),
}};

export default meta;
type Story = StoryObj<{entity_name.capitalize()}Component>;

export const Default: Story = {{
  args: {{}},
}};
"""

        with open(story_path, "w") as f:
            f.write(story_content)

    def _generate_e2e_spec(self, entity, app_path, entity_name):
        """Generates a Cypress E2E test spec for an entity."""
        e2e_path = os.path.join(app_path, "cypress", "e2e")
        os.makedirs(e2e_path, exist_ok=True)

        spec_path = os.path.join(e2e_path, f"{entity_name.lower()}.cy.ts")
        spec_content = f"""
describe('{entity_name.capitalize()} Form', () => {{
  beforeEach(() => {{
    cy.visit('/{entity_name.lower()}');
  }});

  it('should display the form title', () => {{
    cy.get('h2').should('contain', '{entity_name.capitalize()} Form');
  }});

  it('should have a disabled save button initially', () => {{
    cy.get('p-button[label="Save"]').should('be.disabled');
  }});
}});
"""
        with open(spec_path, "w") as f:
            f.write(spec_content)

    def _generate_component_spec(self, entity, component_path, entity_name):
        """Generates a component spec file for a component."""
        spec_path = os.path.join(component_path, f"{entity_name.lower()}.component.spec.ts")

        spec_content = f"""
import {{ ComponentFixture, TestBed }} from '@angular/core/testing';
import {{ ReactiveFormsModule }} from '@angular/forms';
import {{ NoopAnimationsModule }} from '@angular/platform-browser/animations';

import {{ {entity_name.capitalize()}Component }} from './{entity_name.lower()}.component';

describe('{entity_name.capitalize()}Component', () => {{
  let component: {entity_name.capitalize()}Component;
  let fixture: ComponentFixture<{entity_name.capitalize()}Component>;

  beforeEach(async () => {{
    await TestBed.configureTestingModule({{
      imports: [
        ReactiveFormsModule,
        NoopAnimationsModule,
        {entity_name.capitalize()}Component
      ]
    }})
    .compileComponents();

    fixture = TestBed.createComponent({entity_name.capitalize()}Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }});

  it('should create', () => {{
    expect(component).toBeTruthy();
  }});
}});
"""

        with open(spec_path, "w") as f:
            f.write(spec_content)

    def _generate_frontend_dto(self, entity, app_path, entity_name):
        """Generates a TypeScript interface for an entity's DTO."""
        dto_dir = os.path.join(app_path, "src", "app", "core", "models")
        os.makedirs(dto_dir, exist_ok=True)

        dto_path = os.path.join(dto_dir, f"{entity_name.lower()}.dto.ts")

        ts_fields = []
        for col in entity["columns"]:
            ts_type = self._map_ts_type(col['type'])
            ts_fields.append(f"  {col['name']}: {ts_type};")

        ts_fields_str = "\n".join(ts_fields)

        dto_content = f"""
export interface {entity_name.capitalize()}Dto {{
{ts_fields_str}
}}
"""

        with open(dto_path, "w") as f:
            f.write(dto_content)

    def _generate_service(self, entity, app_path, entity_name):
        """Generates an Angular service for an entity."""
        service_dir = os.path.join(app_path, "src", "app", "core", "services")
        os.makedirs(service_dir, exist_ok=True)

        service_path = os.path.join(service_dir, f"{entity_name.lower()}.service.ts")

        entity_name_cap = entity_name.capitalize()
        dto_name = f"{entity_name_cap}Dto"

        service_content = f"""
import {{ Injectable, inject }} from '@angular/core';
import {{ HttpClient }} from '@angular/common/http';
import {{ Observable }} from 'rxjs';
import {{ {dto_name} }} from '../models/{entity_name.lower()}.dto';

@Injectable({{
  providedIn: 'root'
}})
export class {entity_name_cap}Service {{
  private http = inject(HttpClient);
  private apiUrl = '/api/{entity_name.lower()}s';

  getAll(): Observable<{dto_name}[]> {{
    return this.http.get<{dto_name}[]>(this.apiUrl);
  }}

  getById(id: number): Observable<{dto_name}> {{
    return this.http.get<{dto_name}>(`${{this.apiUrl}}/${{id}}`);
  }}

  create(dto: {dto_name}): Observable<{dto_name}> {{
    return this.http.post<{dto_name}>(this.apiUrl, dto);
  }}

  update(id: number, dto: {dto_name}): Observable<{dto_name}> {{
    return this.http.put<{dto_name}>(`${{this.apiUrl}}/${{id}}`, dto);
  }}

  delete(id: number): Observable<void> {{
    return this.http.delete<void>(`${{this.apiUrl}}/${{id}}`);
  }}
}}
"""

        with open(service_path, "w") as f:
            f.write(service_content)

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
        ts_code = f'''import {{ Component, inject }} from '@angular/core';
import {{ RouterModule }} from '@angular/router';
import {{ CommonModule }} from '@angular/common';
import {{ TranslateService, TranslateModule }} from '@ngx-translate/core';

@Component({{
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule, TranslateModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
}})
export class AppComponent {{
  entities = [
    {entity_list}
  ];

  private translate = inject(TranslateService);

  constructor() {{
    this.translate.setDefaultLang('en');
    this.translate.use('en');
  }}
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

        # Add imports for i18n and other providers
        imports_to_add = """import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, HttpClient } from '@angular/common/http';
import { importProvidersFrom } from '@angular/core';
import { TranslateModule, TranslateLoader } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';

export function HttpLoaderFactory(httpClient: HttpClient) {
  return new TranslateHttpLoader(httpClient);
}
"""

        # Prepend the imports to be safe
        content = imports_to_add + content

        # Add providers
        providers_to_add = """
    provideRouter(routes),
    provideAnimations(),
    provideHttpClient(),
    importProvidersFrom(TranslateModule.forRoot({{
      loader: {{
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient]
      }}
    }}))
"""
        if "providers: [" in content:
            content = content.replace(
                "providers: [",
                f"providers: [{providers_to_add},"
            )
        else:
            # This case is unlikely with modern Angular CLI, but as a fallback
            content = content.replace(
                "providers: []",
                f"providers: [{providers_to_add}]"
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

    def _setup_storybook(self, app_path):
        """Initializes Storybook in the generated project."""
        self._log("Setting up Storybook...")
        run_cmd("npx storybook init -y", cwd=app_path)

    def _map_ts_type(self, column_type):
        if column_type == 'string':
            return 'string'
        elif column_type == 'number':
            return 'number'
        else:
            return 'any'

    def _setup_cypress(self, app_path):
        """Sets up Cypress for E2E testing."""
        self._log("Setting up Cypress...")
        # Create cypress.config.ts
        cypress_config_path = os.path.join(app_path, "cypress.config.ts")
        cypress_config_content = """
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:4200',
    specPattern: 'cypress/e2e/**/*.cy.ts',
    supportFile: false,
  },
});
"""
        with open(cypress_config_path, "w") as f:
            f.write(cypress_config_content)

        # Update package.json scripts
        package_json_path = os.path.join(app_path, "package.json")
        with open(package_json_path, "r+") as f:
            package_json = json.load(f)
            if "scripts" not in package_json:
                package_json["scripts"] = {}
            package_json["scripts"]["cy:open"] = "cypress open"
            package_json["scripts"]["cy:run"] = "cypress run"
            f.seek(0)
            json.dump(package_json, f, indent=2)
            f.truncate()

    def _create_proxy_config(self, app_path):
        """Creates a proxy configuration file for the Angular dev server."""
        proxy_config_path = os.path.join(app_path, "proxy.conf.json")

        proxy_config_content = {
          "/api": {
            "target": "http://localhost:8080",
            "secure": False,
            "changeOrigin": True
          }
        }

        with open(proxy_config_path, "w") as f:
            json.dump(proxy_config_content, f, indent=2)

    def _update_angular_json_for_proxy(self, app_path):
        """Updates angular.json to use the proxy configuration."""
        angular_json_path = os.path.join(app_path, "angular.json")

        with open(angular_json_path, "r+") as f:
            angular_json = json.load(f)

            project_name = self.project_config["app"]

            if "projects" in angular_json and project_name in angular_json["projects"]:
                serve_options = angular_json["projects"][project_name]["architect"]["serve"]["options"]
                serve_options["proxyConfig"] = "proxy.conf.json"

            f.seek(0)
            json.dump(angular_json, f, indent=2)
            f.truncate()

    def _generate_translation_files(self, app_path):
        """Generates i18n translation files."""
        i18n_path = os.path.join(app_path, "src", "assets", "i18n")
        os.makedirs(i18n_path, exist_ok=True)

        en_json_path = os.path.join(i18n_path, "en.json")

        translations = {}
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]

        for entity in entities:
            entity_name_upper = entity['name'].upper()
            translations[f"{entity_name_upper}_FORM_TITLE"] = f"{entity['name']} Form"
            for col in entity['columns']:
                col_name_upper = col['name'].upper()
                translations[f"FIELD_{col_name_upper}"] = col['name'].capitalize()

        translations["SAVE_BUTTON"] = "Save"

        with open(en_json_path, "w") as f:
            json.dump(translations, f, indent=2)
