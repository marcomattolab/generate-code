import os
import json

class ProjectInitializer:
    def __init__(self, root_dir, project_file):
        self.root_dir = root_dir
        self.project_file = project_file

    def create_base_structure(self):
        os.makedirs(self.root_dir, exist_ok=True)
        with open(self.project_file, "r") as f:
            project = json.load(f)["project"]
        os.makedirs(os.path.join(self.root_dir, project["frontend"]), exist_ok=True)
        os.makedirs(os.path.join(self.root_dir, project["backend"]), exist_ok=True)
