# FraguaAPI

**FraguaAPI** es una interfaz REST desarrollada con **FastAPI** que permite interactuar con la biblioteca [Fragua](https://pypi.org/project/fragua/) de manera sencilla, modular y extensible.  
Su propósito es ofrecer una capa de comunicación entre servicios o aplicaciones web y la lógica interna de Fragua, permitiendo gestionar *entornos*, *agentes*, *estilos*, *parámetros* a través de endpoints bien definidos.

---

## 🚀 Características

- Arquitectura modular basada en FastAPI.
- Integración directa con la biblioteca `fragua`.
- Endpoints iniciales para:
  - **Environments** (`/environments`)
  - **Agents** (`/agents`)
  - **Styles** (`/styles`)
  - **Params** (`/params`)
- Fácil de extender con servicios personalizados.
- Sin base de datos (usa la estructura interna de Fragua).

---

## 🧩 Estructura del proyecto

```
fraguaAPI/
│
├── fragua_api/
│   ├── main.py
│   ├── routes/
│   │   ├── environment_routes.py
│   │   ├── agent_routes.py
│   │   ├── style_routes.py
│   │   ├── params_routes.py
│   ├── models/
│   │   ├── environment_models.py
│   │   ├── agent_models.py
│   │   ├── style_models.py
│   │   ├── params_models.py
│   ├── services/
│   │   ├── environment_service.py
│   │   ├── agent_service.py
│   │   ├── style_service.py
│   │   ├── params_service.py
│   └── __init__.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalación y uso

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/<tu_usuario>/fraguaAPI.git
cd fraguaAPI
```

### 2️⃣ Crear entorno virtual (opcional pero recomendado)
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

> ⚠️ Asegúrate de tener instalada la biblioteca base:
> ```bash
> pip install fragua
> ```

### 4️⃣ Ejecutar el servidor
```bash
uvicorn fragua_api.main:app --reload
```

La API estará disponible en:
```
http://localhost:8000
```

Y la documentación interactiva (Swagger UI) en:
```
http://localhost:8000/docs
```

---

## 📘 Ejemplo de uso

---

## 🧠 Futuras mejoras

- Persistencia de datos (SQLite / PostgreSQL).
- Autenticación y autorización de usuarios.
- Endpoints avanzados para interacción entre agentes y entornos.
- Dashboard web o panel de control.

---

## 🧑‍💻 Tecnologías utilizadas

- [Python 3.11+](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Fragua](https://pypi.org/project/fragua/)

---

## 🧩 Autor

**Santiago Lanz**  
📍 Desarrollador y creador de Fragua  
🌐 [Portfolio](https://sagodev.github.io/Portfolio-Web-Santiago-Lanz/)  
💼 [LinkedIn](https://www.linkedin.com/in/santiagolanz/)  
🐙 [GitHub](https://github.com/SagoDev)

---

## ⚖️ Licencia

Este proyecto se distribuye bajo la licencia **MIT**.  
Consulta el archivo `LICENSE` para más detalles.
