import os
import json

class ProjectInitializer:
    def __init__(self, root_dir, project_file):
        self.root_dir = root_dir
        self.project_file = project_file

    def create_base_structure(self):
        os.makedirs(self.root_dir, exist_ok=True)

        with open(self.project_file, "r") as f:
            project_config = json.load(f)["project"]
        
        frontend_path = os.path.join(self.root_dir, project_config["frontend"])
        backend_path = os.path.join(self.root_dir, project_config["backend"])
        
        os.makedirs(frontend_path, exist_ok=True)
        os.makedirs(backend_path, exist_ok=True)
