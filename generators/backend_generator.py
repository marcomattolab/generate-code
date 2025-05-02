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
        self._create_basic_structure(backend_path)

    def _create_basic_structure(self, path):
        run_cmd("curl https://start.spring.io/starter.zip -d dependencies=web,data-jpa,h2 -o app.zip", cwd=path)
        run_cmd("unzip app.zip -d .", cwd=path)
        os.remove(os.path.join(path, "app.zip"))
