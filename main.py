from generators.frontend_generator import FrontendGenerator
from generators.backend_generator import BackendGenerator
from generators.project_initializer import ProjectInitializer
import json

class CodeGenerator:
    def __init__(self, entities_file="entities.json", project_file="project.json"):
        self.entities_file = entities_file
        self.project_file = project_file
        with open(self.project_file, "r") as f:
            project = json.load(f)["project"]
            self.root_dir = project["name"]

        self.initializer = ProjectInitializer(self.root_dir ,project_file)
        #self.frontend = FrontendGenerator(root_dir, entities_file)
        #self.backend = BackendGenerator(root_dir, entities_file)

    def generate(self):
        self.initializer.create_base_structure()
        #self.frontend.generate()
        #self.backend.generate()

if __name__ == "__main__":
    generator = CodeGenerator()
    generator.generate()