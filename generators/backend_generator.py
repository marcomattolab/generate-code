import os
import json
from utils import run_cmd

class BackendGenerator:
    def __init__(self, root_dir, entities_file):
        self.root_dir = root_dir
        self.entities_file = entities_file

    def generate(self):
        backend_path = os.path.join(self.root_dir, "backend")
        os.makedirs(backend_path, exist_ok=True)
        self._create_basic_structure(backend_path)

    def _create_basic_structure(self, path):
        run_cmd("curl https://start.spring.io/starter.zip -d dependencies=web,data-jpa,h2 -o app.zip", cwd=path)
        run_cmd("unzip app.zip -d .", cwd=path)
        os.remove(os.path.join(path, "app.zip"))
