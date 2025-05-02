# 🛠️ Code Generator

Un generatore automatico di struttura per progetti frontend e backend a partire da una configurazione JSON.

## 📁 Struttura del progetto

generate-code/\
│\
├── generators/\
│ ├── backend_generator.py\
│ ├── frontend_generator.py\
│ └── project_initializer.py\
│\
├── entities.json\
├── project.json\
├── main.py\
└── .gitignore\


## 🚀 Come funziona

Il progetto legge due file:

- `project.json`: definisce la struttura base del progetto (nomi delle cartelle, nome app).
- `entities.json`: contiene la lista delle entità da cui generare componenti Angular.

E genera:

- 📦 Struttura delle cartelle `frontend/`, `backend/`
- 🧩 Componenti Angular per ogni entità
- 📁 Boilerplate frontend (es. `npm install`, `primeng`, ecc.)

## 🧾 Esempio di `project.json`

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

# Esempio di entities.json
```json
{
  "entities": [
    { "name": "User" },
    { "name": "Product" }
  ]
}
```

# ▶️ Esecuzione
Assicurati di avere Python 3, Node.js, e npm installati.

Posizionati nella root del progetto.

Esegui:
> python3 main.py

⚙️ Dipendenze
Python standard library (os, json)

Node.js & npm per il frontend

📄 License
MIT License
