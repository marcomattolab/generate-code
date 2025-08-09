from generators.frontend_generator import FrontendGenerator
from generators.backend_generator import BackendGenerator
from generators.project_initializer import ProjectInitializer
from generators.cicd_generator import CiCdGenerator
from generators.mobile_generator import MobileGenerator
import json

class CodeGenerator:
    def __init__(self, entities_file="entities.json", project_file="project.json"):
        self.entities_file = entities_file
        self.project_file = project_file
        self.project_config = self._load_project_config()
        self.root_dir = self.project_config["name"]

        self.initializer = ProjectInitializer(self.root_dir ,project_file)
        self.frontend = FrontendGenerator(self.root_dir, entities_file, self.project_config)
        self.backend = BackendGenerator(self.root_dir, entities_file, self.project_config)
        self.cicd = CiCdGenerator(self.root_dir, self.project_config)
        self.mobile = MobileGenerator(self.root_dir, self.project_config)

    def _load_project_config(self):
        with open(self.project_file, "r") as file:
            return json.load(file)["project"]
        
    def generate(self):
        self.initializer.create_base_structure()
        self.frontend.generate()
        self.backend.generate()
        self.cicd.generate()
        self.mobile.generate()

if __name__ == "__main__":
    generator = CodeGenerator()
    generator.generate()