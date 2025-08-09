import os
import yaml
from utils import run_cmd

class MobileGenerator:
    def __init__(self, root_dir, project_config):
        self.root_dir = root_dir
        self.project_config = project_config

    def generate(self):
        self._log("Starting Flutter mobile app generation...")
        self._create_flutter_project()
        self._add_flutter_dependencies()
        self._generate_flutter_files()
        self._log("Flutter mobile app generation complete.")

    def _add_flutter_dependencies(self):
        """Adds http and provider dependencies to pubspec.yaml."""
        app_name = self.project_config["mobile_app"]
        pubspec_path = os.path.join(self.root_dir, "mobile", app_name, "pubspec.yaml")

        self._log("Adding dependencies to pubspec.yaml...")

        with open(pubspec_path, "r") as f:
            pubspec_data = yaml.safe_load(f)

        if "dependencies" not in pubspec_data:
            pubspec_data["dependencies"] = {}

        pubspec_data["dependencies"]["http"] = "^1.1.0"
        pubspec_data["dependencies"]["provider"] = "^6.0.5"

        with open(pubspec_path, "w") as f:
            yaml.dump(pubspec_data, f, default_flow_style=False)

    def _create_flutter_project(self):
        """Creates a new Flutter project."""
        mobile_path = os.path.join(self.root_dir, "mobile")
        os.makedirs(mobile_path, exist_ok=True)
        app_name = self.project_config["mobile_app"]
        self._log(f"Creating Flutter project: {app_name}...")
        run_cmd(f"flutter create {app_name}", cwd=mobile_path)

    def _generate_flutter_files(self):
        """Generates all the necessary files for the Flutter app."""
        app_name = self.project_config["mobile_app"]
        lib_path = os.path.join(self.root_dir, "mobile", app_name, "lib")

        with open("entities.json", "r") as f:
            entities = json.load(f)["entities"]

        for entity in entities:
            entity_name = entity["name"]
            self._log(f"Generating files for {entity_name}...")

            # Create directories
            models_path = os.path.join(lib_path, "models")
            services_path = os.path.join(lib_path, "services")
            providers_path = os.path.join(lib_path, "providers")
            screens_path = os.path.join(lib_path, "screens")
            os.makedirs(models_path, exist_ok=True)
            os.makedirs(services_path, exist_ok=True)
            os.makedirs(providers_path, exist_ok=True)
            os.makedirs(screens_path, exist_ok=True)

            self._generate_flutter_model(entity, models_path)
            self._generate_flutter_service(entity, services_path)
            self._generate_flutter_provider(entity, providers_path)
            self._generate_entity_list_screen(entity, screens_path)

        self._update_main_dart(lib_path, entities)

    def _generate_flutter_model(self, entity, models_path):
        """Generates a Dart model class for an entity."""
        entity_name = entity["name"]
        file_path = os.path.join(models_path, f"{entity_name.lower()}_model.dart")

        fields = []
        for col in entity["columns"]:
            dart_type = self._map_dart_type(col['type'])
            fields.append(f"  final {dart_type} {col['name']};")

        fields_str = "\n".join(fields)

        constructor_params = ",\n".join([f"    required this.{col['name']}" for col in entity["columns"]])

        model_content = f"""
class {entity_name} {{
{fields_str}

  {entity_name}({{
{constructor_params}
  }});

  factory {entity_name}.fromJson(Map<String, dynamic> json) {{
    return {entity_name}(
      {', '.join([f"{col['name']}: json['{col['name']}']" for col in entity["columns"]])}
    );
  }}
}}
"""
        with open(file_path, "w") as f:
            f.write(model_content)

    def _generate_flutter_service(self, entity, services_path):
        """Generates a Dart service class for an entity."""
        entity_name = entity["name"]
        file_path = os.path.join(services_path, f"{entity_name.lower()}_service.dart")

        service_content = f"""
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/{entity_name.lower()}_model.dart';

class {entity_name}Service {{
  final String _baseUrl = 'http://10.0.2.2:8080/api/{entity_name.lower()}s'; // 10.0.2.2 for Android emulator

  Future<List<{entity_name}>> getAll() async {{
    final response = await http.get(Uri.parse(_baseUrl));
    if (response.statusCode == 200) {{
      List<dynamic> data = json.decode(response.body);
      return data.map((json) => {entity_name}.fromJson(json)).toList();
    }} else {{
      throw Exception('Failed to load {entity_name.lower()}s');
    }}
  }}
}}
"""
        with open(file_path, "w") as f:
            f.write(service_content)

    def _generate_flutter_provider(self, entity, providers_path):
        """Generates a Dart provider class for an entity."""
        entity_name = entity["name"]
        file_path = os.path.join(providers_path, f"{entity_name.lower()}_provider.dart")

        provider_content = f"""
import 'package:flutter/material.dart';
import '../models/{entity_name.lower()}_model.dart';
import '../services/{entity_name.lower()}_service.dart';

class {entity_name}Provider with ChangeNotifier {{
  final _{entity_name}Service = {entity_name}Service();
  List<{entity_name}> _{entity_name.lower()}s = [];
  bool _isLoading = false;

  List<{entity_name}> get {entity_name.lower()}s => _{entity_name.lower()}s;
  bool get isLoading => _isLoading;

  Future<void> fetch{entity_name}s() async {{
    _isLoading = true;
    notifyListeners();
    try {{
      _{entity_name.lower()}s = await _{entity_name}Service.getAll();
    }} catch (error) {{
      // Handle error
    }} finally {{
      _isLoading = false;
      notifyListeners();
    }}
  }}
}}
"""
        with open(file_path, "w") as f:
            f.write(provider_content)

    def _generate_entity_list_screen(self, entity, screens_path):
        """Generates a Flutter screen to list entities."""
        entity_name = entity["name"]
        file_path = os.path.join(screens_path, f"{entity_name.lower()}_list_screen.dart")

        list_screen_content = f"""
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/{entity_name.lower()}_provider.dart';

class {entity_name}ListScreen extends StatefulWidget {{
  @override
  _{entity_name}ListScreenState createState() => _{entity_name}ListScreenState();
}}

class _{entity_name}ListScreenState extends State<{entity_name}ListScreen> {{
  @override
  void initState() {{
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {{
      Provider.of<{entity_name}Provider>(context, listen: false).fetch{entity_name}s();
    }});
  }}

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: Text('{entity_name}s'),
      ),
      body: Consumer<{entity_name}Provider>(
        builder: (context, provider, child) {{
          if (provider.isLoading) {{
            return Center(child: CircularProgressIndicator());
          }}
          return ListView.builder(
            itemCount: provider.{entity_name.lower()}s.length,
            itemBuilder: (context, index) {{
              final item = provider.{entity_name.lower()}s[index];
              return ListTile(
                title: Text(item.name), // Assumes a 'name' field
              );
            }},
          );
        }},
      ),
    );
  }}
}}
"""
        with open(file_path, "w") as f:
            f.write(list_screen_content)

    def _update_main_dart(self, lib_path, entities):
        """Updates the main.dart file to set up providers and routes."""
        main_dart_path = os.path.join(lib_path, "main.dart")

        provider_imports = "\n".join([f"import 'providers/{entity['name'].lower()}_provider.dart';" for entity in entities])
        screen_imports = "\n".join([f"import 'screens/{entity['name'].lower()}_list_screen.dart';" for entity in entities])

        providers = ",\n        ".join([f"ChangeNotifierProvider(create: (_) => {entity['name']}Provider())" for entity in entities])

        routes = ",\n        ".join([f"'/{{entity['name'].lower()}}s': (context) => {entity['name']}ListScreen()" for entity in entities])

        home_screen_buttons = "\n".join([f"""
            ElevatedButton(
              child: Text('View {entity['name']}s'),
              onPressed: () => Navigator.pushNamed(context, '/{entity['name'].lower()}s'),
            ),""" for entity in entities])

        main_dart_content = f\"\"\"
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
{provider_imports}
{screen_imports}

void main() {{
  runApp(MyApp());
}}

class MyApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return MultiProvider(
      providers: [
        {providers}
      ],
      child: MaterialApp(
        title: 'Flutter App',
        theme: ThemeData(
          primarySwatch: Colors.blue,
        ),
        home: HomeScreen(),
        routes: {{
          {routes}
        }},
      ),
    );
  }}
}}

class HomeScreen extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: Text('Home'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            {home_screen_buttons}
          ],
        ),
      ),
    );
  }}
}}
\"\"\"
        with open(main_dart_path, "w") as f:
            f.write(main_dart_content)

    def _map_dart_type(self, column_type):
        if column_type == 'string':
            return 'String'
        elif column_type == 'number':
            return 'int' # Or double
        else:
            return 'dynamic'

    def _log(self, message):
        print(f"[MobileGenerator] {message}")
