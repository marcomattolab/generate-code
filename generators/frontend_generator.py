import os
import json
from utils import run_cmd

class FrontendGenerator:
    def __init__(self, root_dir, entities_file, project_config):
        self.root_dir = root_dir
        self.entities_file = entities_file
        self.project_config = project_config
        self.frontend_config = self.project_config['frontend']
        self.framework = self.frontend_config['framework']
        self.frontend_dir = os.path.join(self.root_dir, self.frontend_config['name'])
        self.app_name = self.project_config["app"]
        self.app_path = os.path.join(self.frontend_dir, self.app_name)

    def _log(self, message):
        print(f"[FrontendGenerator] {message}")

    def generate(self):
        os.makedirs(self.frontend_dir, exist_ok=True)

        if self.framework == 'angular':
            self._generate_angular()
        elif self.framework == 'react':
            self._generate_react()
        else:
            raise ValueError(f"Unsupported frontend framework: {self.framework}")

    def _generate_react(self):
        """Generates a complete React application."""
        self._log("Generating React application...")

        # 1. Create React App
        run_cmd(
            f"npx create-react-app {self.app_name}",
            cwd=self.frontend_dir
        )
        if not os.path.exists(self.app_path):
            raise FileNotFoundError("React project not found. 'create-react-app' might have failed.")

        # 2. Install dependencies
        run_cmd("npm install axios react-router-dom", cwd=self.app_path)

        # 3. Create folder structure
        os.makedirs(os.path.join(self.app_path, "src", "components"), exist_ok=True)
        os.makedirs(os.path.join(self.app_path, "src", "services"), exist_ok=True)

        # 4. Generate files
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]

        for entity in entities:
            self._generate_react_component(entity)
            self._generate_react_service(entity)

        self._generate_react_app_js(entities)
        self._generate_react_index_css()

    def _generate_react_component(self, entity):
        name_cap = entity["name"]
        name_lower = entity["name"].lower()

        component_content = f\"\"\"
import React, {{ useState, useEffect }} from 'react';
import {{ getAll }} from '../services/{name_lower}Service';

const {name_cap}List = () => {{
    const [{name_lower}s, set{name_cap}s] = useState([]);

    useEffect(() => {{
        getAll().then(response => {{
            set{name_cap}s(response.data);
        }});
    }}, []);

    return (
        <div>
            <h2>{name_cap} List</h2>
            <ul>
                {{ {name_lower}s.map({name_lower} => <li key={{ {name_lower}.id }}>{{ {name_lower}.name }}</li>) }}
            </ul>
        </div>
    );
}};

export default {name_cap}List;
\"\"\"
        component_path = os.path.join(self.app_path, "src", "components", f"{name_cap}List.js")
        with open(component_path, "w") as f:
            f.write(component_content)

    def _generate_react_service(self, entity):
        name_lower = entity["name"].lower()

        service_content = f\"\"\"
import axios from 'axios';

const API_URL = '/api/{name_lower}s';

export const getAll = () => {{
    return axios.get(API_URL);
}};
\"\"\"
        service_path = os.path.join(self.app_path, "src", "services", f"{name_lower}Service.js")
        with open(service_path, "w") as f:
            f.write(service_content)

    def _generate_react_app_js(self, entities):
        imports = "\\n".join([f"import {e['name']}List from './components/{e['name']}List.js';" for e in entities])
        links = "\\n".join([f'              <li><Link to="/{e["name"].lower()}">{e["name"]}</Link></li>' for e in entities])
        routes = "\\n".join([f'          <Route path="/{e["name"].lower()}" element={{<{e["name"]}List />}} />' for e in entities])

        app_js_content = f\"\"\"
import React from 'react';
import {{ BrowserRouter as Router, Route, Link, Routes }} from 'react-router-dom';
import './index.css';
{imports}

function App() {{
    return (
        <Router>
            <div className="App">
                <nav>
                    <ul>
{links}
                    </ul>
                </nav>
                <main>
                    <Routes>
{routes}
                    </Routes>
                </main>
            </div>
        </Router>
    );
}}

export default App;
\"\"\"
        app_js_path = os.path.join(self.app_path, "src", "App.js")
        with open(app_js_path, "w") as f:
            f.write(app_js_content)

    def _generate_react_index_css(self):
        css_content = \"\"\"
body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }}
.App {{ display: flex; }}
nav {{ width: 200px; background: #f0f0f0; padding: 20px; height: 100vh; }}
nav ul {{ list-style-type: none; padding: 0; }}
nav ul li {{ margin-bottom: 10px; }}
nav ul li a {{ text-decoration: none; color: #333; }}
main {{ flex-grow: 1; padding: 20px; }}
\"\"\"
        css_path = os.path.join(self.app_path, "src", "index.css")
        with open(css_path, "w") as f:
            f.write(css_content)

    def _generate_angular(self):
        """Generates a complete Angular application."""
        run_cmd(
            f"npx -y @angular/cli@latest new {self.app_name} --style=scss --routing=false --skip-git --skip-install",
            cwd=self.frontend_dir,
        )

        if not os.path.exists(self.app_path):
            raise FileNotFoundError("Angular project not found. Check if 'app' was created.")

        self._install_angular_dependencies(self.app_path)
        self._generate_angular_app_component(self.app_path)
        self._generate_angular_components(self.app_path)
        self._update_angular_app_config(self.app_path)
        self._update_angular_styles(self.app_path)
        self._setup_angular_cypress(self.app_path)
        self._create_angular_proxy_config(self.app_path)
        self._update_angular_json(self.app_path)
        self._generate_angular_translation_files(self.app_path)
        self._generate_tailwind_config(self.app_path)
        self._add_compodoc_script(self.app_path)
        self._generate_angular_environment_files(self.app_path)

        if self.project_config.get("features", {}).get("authentication"):
            self._generate_angular_auth_files(self.app_path)
            self._generate_angular_auth_interceptor(self.app_path)
            self._generate_angular_auth_guard(self.app_path)

    def _install_angular_dependencies(self, path):
        deps = ["primeng", "primeicons", "primeflex", "@angular/animations", "@angular/forms", "@ngx-translate/core", "@ngx-translate/http-loader"]
        if self.project_config.get("features", {}).get("authentication"):
            deps.append("angular-oauth2-oidc")
        run_cmd(f"npm install {' '.join(deps)}", cwd=path)
        dev_deps = ["@storybook/angular", "@storybook/cli", "@angular-eslint/schematics", "prettier", "cypress", "tailwindcss", "@compodoc/compodoc"]
        run_cmd(f"npm install --save-dev {' '.join(dev_deps)}", cwd=path)

    def _generate_angular_components(self, path):
        with open(self.entities_file, "r") as f:
            entities = json.load(f)["entities"]
        components_dir = os.path.join(path, "src", "app", "components")
        os.makedirs(components_dir, exist_ok=True)
        for entity in entities:
            name = entity["name"].lower()
            entity_path = os.path.join(components_dir, name)
            os.makedirs(entity_path, exist_ok=True)
            with open(os.path.join(entity_path, f"{name}.component.ts"), "w") as f:
                f.write(self._generate_angular_component_code(entity))
            with open(os.path.join(entity_path, f"{name}.component.html"), "w") as f:
                f.write(self._generate_angular_component_html(entity))
            self._generate_angular_story(entity, entity_path, entity['name'])
            self._generate_angular_component_spec(entity, entity_path, entity['name'])
            self._generate_frontend_dto(entity, path, entity['name'])
            self._generate_angular_service(entity, path, entity['name'])
            self._generate_angular_e2e_spec(entity, path, entity['name'])
        routes_file_path = os.path.join(path, "src", "app", "app.routes.ts")
        with open(routes_file_path, "w") as f:
            f.write(self._generate_angular_entities_routes(entities))

    def _generate_angular_component_code(self, entity):
        class_name = entity["name"].capitalize()
        entity_name_lower = entity["name"].lower()
        service_name = f"{class_name}Service"
        form_controls = [f'"{col["name"]}": ["", [Validators.required]]' for col in entity["columns"] if col["name"].lower() != 'id']
        form_controls_str = ",\n    ".join(form_controls)
        primeng_imports = {"ButtonModule": "primeng/button", "InputTextModule": "primeng/inputtext"}
        if any(col.get("type") == "number" for col in entity["columns"] if col.get("name", "").lower() != "id"):
            primeng_imports["InputNumberModule"] = "primeng/inputnumber"
        import_statements = [f"import {{ {mod} }} from '{path}';" for mod, path in primeng_imports.items()]
        primeng_imports_str = "\n".join(import_statements)
        primeng_modules_str = ", ".join(primeng_imports.keys())
        return f"import {{ Component, inject, OnInit }} from '@angular/core';\nimport {{ FormBuilder, ReactiveFormsModule, Validators }} from '@angular/forms';\nimport {{ CommonModule }} from '@angular/common';\nimport {{ {service_name} }} from '../../core/services/{entity_name_lower}.service';\n{primeng_imports_str}\n\n@Component({{\n  selector: 'app-{entity_name_lower}',\n  standalone: true,\n  imports: [CommonModule, ReactiveFormsModule, {primeng_modules_str}],\n  templateUrl: './{entity_name_lower}.component.html'\n}})\nexport class {class_name}Component implements OnInit {{\n  private fb = inject(FormBuilder);\n  public {entity_name_lower}Service = inject({service_name});\n  form = this.fb.group({{ {form_controls_str} }});\n  ngOnInit() {{ this.{entity_name_lower}Service.getAll(); }}\n  save(): void {{\n    if (this.form.invalid) {{ this.form.markAllAsTouched(); return; }}\n    this.{entity_name_lower}Service.create(this.form.value as any);\n    this.form.reset();\n  }}\n}}"

    def _generate_angular_component_html(self, entity):
        inputs = []
        entity_name_upper = entity['name'].upper()
        for col in entity["columns"]:
            if col["name"].lower() == 'id': continue
            input_html = f'<p-inputNumber inputId="{col["name"]}" formControlName="{col["name"]}" mode="decimal" [showButtons]="true"></p-inputNumber>' if col.get("type") == 'number' else f'<input id="{col["name"]}" type="text" pInputText formControlName="{col["name"]}" />'
            inputs.append(f'<div class="field col-12"><label for="{col["name"]}" class="font-semibold">{{{{ \\'FIELD_{col["name"].upper()}\\' | translate }}}}</label>{input_html}</div>')
        return f'<div class="card p-fluid"><h2 class="text-2xl font-bold mb-4">{{{{ \\'{entity_name_upper}_FORM_TITLE\\' | translate }}}}</h2><form [formGroup]="form" (ngSubmit)="save()"><div class="formgrid grid">{"".join(inputs)}</div><div class="mt-4 flex justify-content-end"><p-button label="{{{{ \\'SAVE_BUTTON\\' | translate }}}}" type="submit" icon="pi pi-check" [disabled]="form.invalid"></p-button></div></form></div>'

    def _generate_angular_story(self, entity, component_path, entity_name):
        story_path = os.path.join(component_path, f"{entity_name.lower()}.stories.ts")
        story_content = f"import type {{ Meta, StoryObj }} from '@storybook/angular';\nimport {{ {entity_name.capitalize()}Component }} from './{entity_name.lower()}.component';\n\nconst meta: Meta<{entity_name.capitalize()}Component> = {{ title: 'Components/{entity_name.capitalize()}', component: {entity_name.capitalize()}Component, tags: ['autodocs'], render: (args: {entity_name.capitalize()}Component) => ({{ props: {{ ...args }} }}) }};\nexport default meta;\ntype Story = StoryObj<{entity_name.capitalize()}Component>;\nexport const Default: Story = {{ args: {{}} }};"
        with open(story_path, "w") as f: f.write(story_content)

    def _generate_angular_e2e_spec(self, entity, app_path, entity_name):
        e2e_path = os.path.join(app_path, "cypress", "e2e")
        os.makedirs(e2e_path, exist_ok=True)
        spec_path = os.path.join(e2e_path, f"{entity_name.lower()}.cy.ts")
        spec_content = f"describe('{entity_name.capitalize()} Form', () => {{\n  beforeEach(() => cy.visit('/{entity_name.lower()}'));\n  it('should display the form title', () => cy.get('h2').should('contain', '{entity_name.capitalize()} Form'));\n  it('should have a disabled save button initially', () => cy.get('p-button[label=\"Save\"]').should('be.disabled'));\n}});"
        with open(spec_path, "w") as f: f.write(spec_content)

    def _generate_angular_component_spec(self, entity, component_path, entity_name):
        spec_path = os.path.join(component_path, f"{entity_name.lower()}.component.spec.ts")
        spec_content = f"import {{ ComponentFixture, TestBed }} from '@angular/core/testing';\nimport {{ ReactiveFormsModule }} from '@angular/forms';\nimport {{ NoopAnimationsModule }} from '@angular/platform-browser/animations';\nimport {{ {entity_name.capitalize()}Component }} from './{entity_name.lower()}.component';\n\ndescribe('{entity_name.capitalize()}Component', () => {{\n  let component: {entity_name.capitalize()}Component;\n  let fixture: ComponentFixture<{entity_name.capitalize()}Component>;\n  beforeEach(async () => {{\n    await TestBed.configureTestingModule({{ imports: [ReactiveFormsModule, NoopAnimationsModule, {entity_name.capitalize()}Component] }}).compileComponents();\n    fixture = TestBed.createComponent({entity_name.capitalize()}Component);\n    component = fixture.componentInstance;\n    fixture.detectChanges();\n  }});\n  it('should create', () => expect(component).toBeTruthy());\n}});"
        with open(spec_path, "w") as f: f.write(spec_content)

    def _generate_frontend_dto(self, entity, app_path, entity_name):
        dto_dir = os.path.join(app_path, "src", "app", "core", "models")
        os.makedirs(dto_dir, exist_ok=True)
        dto_path = os.path.join(dto_dir, f"{entity_name.lower()}.dto.ts")
        ts_fields = [f"  {col['name']}: {self._map_ts_type(col['type'])};" for col in entity["columns"]]
        dto_content = f"export interface {entity_name.capitalize()}Dto {{\n{chr(10).join(ts_fields)}\n}}"
        with open(dto_path, "w") as f: f.write(dto_content)

    def _generate_angular_service(self, entity, app_path, entity_name):
        service_dir = os.path.join(app_path, "src", "app", "core", "services")
        os.makedirs(service_dir, exist_ok=True)
        service_path = os.path.join(service_dir, f"{entity_name.lower()}.service.ts")
        entity_name_cap, dto_name = entity_name.capitalize(), f"{entity_name.capitalize()}Dto"
        service_content = f"import {{ Injectable, inject, signal }} from '@angular/core';\nimport {{ HttpClient }} from '@angular/common/http';\nimport {{ tap }} from 'rxjs/operators';\nimport {{ {dto_name} }} from '../models/{entity_name.lower()}.dto';\nimport {{ environment }} from '../../../../environments/environment';\n\n@Injectable({{ providedIn: 'root' }})\nexport class {entity_name_cap}Service {{\n  private http = inject(HttpClient);\n  private apiUrl = `${{environment.apiUrl}}/{entity_name.lower()}s`;\n  items = signal<{dto_name}[]>([]);\n  loading = signal<boolean>(false);\n  getAll() {{ this.loading.set(true); this.http.get<{dto_name}[]>(this.apiUrl).pipe(tap(items => {{ this.items.set(items); this.loading.set(false); }})).subscribe(); }}\n  create(dto: {dto_name}) {{ this.loading.set(true); this.http.post<{dto_name}>(this.apiUrl, dto).pipe(tap(newItem => {{ this.items.update(items => [...items, newItem]); this.loading.set(false); }})).subscribe(); }}\n  update(id: number, dto: {dto_name}) {{ this.loading.set(true); this.http.put<{dto_name}>(`${{this.apiUrl}}/${{id}}`, dto).pipe(tap(updatedItem => {{ this.items.update(items => items.map(item => item.id === id ? updatedItem : item)); this.loading.set(false); }})).subscribe(); }}\n  delete(id: number) {{ this.loading.set(true); this.http.delete<void>(`${{this.apiUrl}}/${{id}}`).pipe(tap(() => {{ this.items.update(items => items.filter(item => item.id !== id)); this.loading.set(false); }})).subscribe(); }}\n}}"
        with open(service_path, "w") as f: f.write(service_content)

    def _generate_angular_entities_routes(self, entities):
        if not entities: return "import { Routes } from '@angular/router';\n\nexport const routes: Routes = [];"
        first_entity_path = entities[0]["name"].lower()
        auth_enabled = self.project_config.get("features", {}).get("authentication")
        imports = ["import { Routes } from '@angular/router';"]
        if auth_enabled: imports.append("import { authGuard } from './core/guards/auth.guard';")
        can_activate_str = ", canActivate: [authGuard]" if auth_enabled else ""
        routes = [f"{{ path: '{e['name'].lower()}', loadComponent: () => import('./components/{e['name'].lower()}/{e['name'].lower()}.component').then(m => m.{e['name'].capitalize()}Component){can_activate_str} }}" for e in entities]
        return f"{chr(10).join(imports)}\n\nexport const routes: Routes = [\n  {{ path: '', redirectTo: '{first_entity_path}', pathMatch: 'full' }},\n  {f',{chr(10)}  '.join(routes)}\n];"

    def _generate_angular_app_component(self, path):
        with open(self.entities_file, "r") as f: entities = json.load(f)["entities"]
        src_app_dir = os.path.join(path, "src", "app")
        os.makedirs(src_app_dir, exist_ok=True)
        auth_enabled = self.project_config.get("features", {}).get("authentication")
        entity_list = ", ".join([f"{{ name: '{e['name'].capitalize()}', path: '/{e['name'].lower()}' }}" for e in entities])
        ts_imports = ["import {{ Component, inject }} from '@angular/core';", "import {{ RouterModule }} from '@angular/router';", "import {{ CommonModule }} from '@angular/common';", "import {{ TranslateService, TranslateModule }} from '@ngx-translate/core';"]
        ts_class_members = [f"  entities = [{entity_list}];", "  private translate = inject(TranslateService);"]
        constructor_body = "this.translate.setDefaultLang('en'); this.translate.use('en');"
        if auth_enabled:
            ts_imports.append("import {{ AuthService }} from './core/auth/auth.service';")
            ts_class_members.insert(0, "  authService = inject(AuthService);")
        ts_code = f"{chr(10).join(ts_imports)}\n\n@Component({{ selector: 'app-root', standalone: true, imports: [CommonModule, RouterModule, TranslateModule], templateUrl: './app.component.html', styleUrls: ['./app.component.scss'] }})\nexport class AppComponent {{\n{chr(10).join(ts_class_members)}\n\n  constructor() {{ {constructor_body} }}\n}}"
        with open(os.path.join(src_app_dir, "app.component.ts"), "w") as f: f.write(ts_code)
        auth_buttons_html = ""
        if auth_enabled: auth_buttons_html = "<div class=\"mt-auto\">@if (authService.isLoggedIn) { <div class=\"p-2 text-center\"><span>{{ authService.username }}</span><button (click)=\"authService.logout()\" class=\"w-full mt-2 p-2 bg-red-600 rounded\">Logout</button></div> } @else { <div class=\"p-2 text-center\"><button (click)=\"authService.login()\" class=\"w-full p-2 bg-green-600 rounded\">Login</button></div> }</div>"
        html_code = f'<div class="flex h-screen bg-gray-100 font-sans\"><div class="w-64 bg-gray-800 text-white p-5 flex flex-col shadow-lg\"><div><div class="text-2xl font-bold mb-10 text-center"><a routerLink=\"/\" class=\"text-white no-underline\">App</a></div><nav><ul class="space-y-2">@for (entity of entities; track entity.name) {{ <li><a [routerLink]=\"entity.path\" routerLinkActive=\"active-link\" class=\"flex items-center p-2 text-base font-normal text-gray-200 rounded-lg hover:bg-gray-700 transition-colors duration-200\"><span class=\"ml-3\">{{{{ entity.name }}}}</span></a></li> }}</ul></nav></div>{auth_buttons_html}</div><main class=\"flex-1 p-10 overflow-y-auto\"><div class=\"bg-white p-8 rounded-lg shadow-md\"><router-outlet></router-outlet></div></main></div>'
        with open(os.path.join(src_app_dir, "app.component.html"), "w") as f: f.write(html_code)
        with open(os.path.join(src_app_dir, "app.component.scss"), "w") as f: f.write(".active-link { background-color: #4f46e5; color: white; }")

    def _update_angular_app_config(self, app_path):
        app_config_path = os.path.join(app_path, "src", "app", "app.config.ts")
        with open(app_config_path, "r") as f: content = f.read()
        imports_to_add = "import { provideRouter } from '@angular/router';\nimport { routes } from './app.routes';\nimport { provideAnimations } from '@angular/platform-browser/animations';\nimport { provideHttpClient, HttpClient, withInterceptorsFromDi } from '@angular/common/http';\nimport { importProvidersFrom } from '@angular/core';\nimport { TranslateModule, TranslateLoader } from '@ngx-translate/core';\nimport { TranslateHttpLoader } from '@ngx-translate/http-loader';\nimport { environment } from '../environments/environment';"
        if self.project_config.get("features", {}).get("authentication"):
            imports_to_add += "\nimport { OAuthService } from 'angular-oauth2-oidc';\nimport { AuthInterceptor } from './core/interceptors/auth.interceptor';\nimport { HTTP_INTERCEPTORS } from '@angular/common/http';"
        imports_to_add += "\n\nexport function HttpLoaderFactory(httpClient: HttpClient) {\n  return new TranslateHttpLoader(httpClient);\n}"
        content = imports_to_add + content
        providers = ["provideRouter(routes)", "provideAnimations()", "provideHttpClient(withInterceptorsFromDi())", "importProvidersFrom(TranslateModule.forRoot({ loader: { provide: TranslateLoader, useFactory: HttpLoaderFactory, deps: [HttpClient] } }))"]
        if self.project_config.get("features", {}).get("authentication"):
            providers.extend(["OAuthService", "{ provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }"])
        providers_str = ",\n    ".join(providers)
        content = content.replace("providers: [", f"providers: [{providers_str},")
        with open(app_config_path, "w") as f: f.write(content)

    def _update_angular_styles(self, app_path):
        styles_path = os.path.join(app_path, "src", "styles.scss")
        final_styles = "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n@import \"primeng/resources/themes/lara-light-blue/theme.css\";\n@import \"primeng/resources/primeng.css\";\n@import \"primeicons/primeicons.css\";\n@import \"primeflex/primeflex.css\";"
        with open(styles_path, "w") as f: f.write(final_styles)

    def _setup_angular_cypress(self, app_path):
        self._log("Setting up Cypress...")
        cypress_config_path = os.path.join(app_path, "cypress.config.ts")
        cypress_config_content = "import { defineConfig } from 'cypress';\n\nexport default defineConfig({ e2e: { baseUrl: 'http://localhost:4200', specPattern: 'cypress/e2e/**/*.cy.ts', supportFile: false } });"
        with open(cypress_config_path, "w") as f: f.write(cypress_config_content)
        package_json_path = os.path.join(app_path, "package.json")
        with open(package_json_path, "r+") as f:
            package_json = json.load(f)
            package_json.setdefault("scripts", {})
            package_json["scripts"]["cy:open"] = "cypress open"
            package_json["scripts"]["cy:run"] = "cypress run"
            f.seek(0); json.dump(package_json, f, indent=2); f.truncate()

    def _map_ts_type(self, column_type):
        return 'number' if column_type == 'number' else 'string'

    def _generate_angular_environment_files(self, app_path):
        env_path = os.path.join(app_path, "src", "environments")
        os.makedirs(env_path, exist_ok=True)
        with open(os.path.join(env_path, "environment.ts"), "w") as f: f.write("export const environment = { production: false, apiUrl: '/api' };")
        with open(os.path.join(env_path, "environment.prod.ts"), "w") as f: f.write("export const environment = { production: true, apiUrl: 'https://your-production-api.com/api' };")

    def _generate_angular_auth_files(self, app_path):
        auth_path = os.path.join(app_path, "src", "app", "core", "auth")
        os.makedirs(auth_path, exist_ok=True)
        auth_config_content = "import { AuthConfig } from 'angular-oauth2-oidc';\n\nexport const authConfig: AuthConfig = { issuer: 'http://localhost:8081/realms/myrealm', redirectUri: window.location.origin, clientId: 'my-angular-app', responseType: 'code', scope: 'openid profile email', showDebugInformation: true };"
        with open(os.path.join(auth_path, "auth.config.ts"), "w") as f: f.write(auth_config_content)
        auth_service_content = "import { Injectable, inject } from '@angular/core';\nimport { OAuthService } from 'angular-oauth2-oidc';\nimport { authConfig } from './auth.config';\n\n@Injectable({ providedIn: 'root' })\nexport class AuthService {\n  private oauthService = inject(OAuthService);\n  constructor() { this.oauthService.configure(authConfig); this.oauthService.loadDiscoveryDocumentAndTryLogin(); }\n  login() { this.oauthService.initCodeFlow(); }\n  logout() { this.oauthService.logOut(); }\n  get isLoggedIn(): boolean { return this.oauthService.hasValidAccessToken(); }\n  get username(): string { const claims = this.oauthService.getIdentityClaims(); return claims ? claims['preferred_username'] : ''; }\n}"
        with open(os.path.join(auth_path, "auth.service.ts"), "w") as f: f.write(auth_service_content)

    def _generate_angular_auth_interceptor(self, app_path):
        interceptor_path = os.path.join(app_path, "src", "app", "core", "interceptors")
        os.makedirs(interceptor_path, exist_ok=True)
        interceptor_content = "import { Injectable, inject } from '@angular/core';\nimport { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';\nimport { Observable } from 'rxjs';\nimport { OAuthService } from 'angular-oauth2-oidc';\n\n@Injectable()\nexport class AuthInterceptor implements HttpInterceptor {\n  private oauthService = inject(OAuthService);\n  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {\n    const token = this.oauthService.getAccessToken();\n    if (token) {\n      const cloned = req.clone({ headers: req.headers.set('Authorization', 'Bearer ' + token) });\n      return next.handle(cloned);\n    }\n    return next.handle(req);\n  }\n}"
        with open(os.path.join(interceptor_path, "auth.interceptor.ts"), "w") as f: f.write(interceptor_content)

    def _generate_angular_auth_guard(self, app_path):
        guards_path = os.path.join(app_path, "src", "app", "core", "guards")
        os.makedirs(guards_path, exist_ok=True)
        guard_content = "import { inject } from '@angular/core';\nimport { CanActivateFn, Router } from '@angular/router';\nimport { AuthService } from '../auth/auth.service';\n\nexport const authGuard: CanActivateFn = (route, state) => {\n  const authService = inject(AuthService);\n  const router = inject(Router);\n  if (authService.isLoggedIn) { return true; }\n  authService.login();\n  return false;\n};"
        with open(os.path.join(guards_path, "auth.guard.ts"), "w") as f: f.write(guard_content)

    def _create_angular_proxy_config(self, app_path):
        proxy_config_path = os.path.join(app_path, "proxy.conf.json")
        with open(proxy_config_path, "w") as f: json.dump({"/api": {"target": "http://localhost:8080", "secure": False, "changeOrigin": True}}, f, indent=2)

    def _update_angular_json(self, app_path):
        angular_json_path = os.path.join(app_path, "angular.json")
        with open(angular_json_path, "r+") as f:
            angular_json = json.load(f)
            project_name = self.project_config["app"]
            if "projects" in angular_json and project_name in angular_json["projects"]:
                serve_options = angular_json["projects"][project_name]["architect"]["serve"]["options"]
                serve_options["proxyConfig"] = "proxy.conf.json"
                build_prod_config = angular_json["projects"][project_name]["architect"]["build"]["configurations"]["production"]
                build_prod_config.setdefault("fileReplacements", []).append({"replace": "src/environments/environment.ts", "with": "src/environments/environment.prod.ts"})
            f.seek(0); json.dump(angular_json, f, indent=2); f.truncate()

    def _generate_angular_translation_files(self, app_path):
        i18n_path = os.path.join(app_path, "src", "assets", "i18n")
        os.makedirs(i18n_path, exist_ok=True)
        en_json_path = os.path.join(i18n_path, "en.json")
        with open(self.entities_file, "r") as f: entities = json.load(f)["entities"]
        translations = {f"{e['name'].upper()}_FORM_TITLE": f"{e['name']} Form" for e in entities}
        for e in entities:
            for col in e['columns']:
                translations[f"FIELD_{col['name'].upper()}"] = col['name'].capitalize()
        translations["SAVE_BUTTON"] = "Save"
        with open(en_json_path, "w") as f: json.dump(translations, f, indent=2)

    def _generate_tailwind_config(self, app_path):
        config_path = os.path.join(app_path, "tailwind.config.js")
        config_content = "module.exports = { content: ['./src/**/*.{html,ts}'], theme: { extend: {} }, plugins: [] };"
        with open(config_path, "w") as f: f.write(config_content)

    def _add_compodoc_script(self, app_path):
        package_json_path = os.path.join(app_path, "package.json")
        with open(package_json_path, "r+") as f:
            package_json = json.load(f)
            package_json.setdefault("scripts", {})
            package_json["scripts"]["compodoc"] = "npx compodoc -p src/tsconfig.app.json -s"
            f.seek(0); json.dump(package_json, f, indent=2); f.truncate()
