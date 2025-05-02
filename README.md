# 🛠️ Code Generator

An automatic structure generator for frontend and backend projects based on a JSON configuration.


## 📁 Project structure

generate-code/\
│
├── generators/\
│ ├── backend_generator.py\
│ ├── frontend_generator.py\
│ └── project_initializer.py\
│
├── entities.json\
├── project.json\
├── main.py\
└── .gitignore\


## 🚀 How It Works

The project reads two files:

- `project.json`: defines the basic project structure (folder names, app name).
- `entities.json`: contains the list of entities to generate Angular components for.

It then generates:

- 📦 Folder structure for `frontend/` and `backend/`
- 🧩 Angular components for each entity
- 📁 Frontend boilerplate (e.g., `npm install`, `primeng`, etc.)

## 🧾 Example `project.json`

```json
{
  "project": {
    "name": "generated_app",
    "app": "app",
    "backend": "backend",
    "frontend": "frontend"
  }
}
```

## 🧾 Example of entities.json

```json
{
  "entities": [
    { "name": "User" },
    { "name": "Product" }
  ]
}
```

# ▶️ How to Run
Make sure you have Python 3, Node.js, and npm installed.

Navigate to the root of the project, then run:

> python3 main.py


# 📄 License
MIT License
