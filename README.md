# Fragua

Fragua es una biblioteca ligera y modular diseñada para construir
pipelines ETL/ELT y flujos de procesamiento de datos en Python.
Proporciona componentes reutilizables como entornos, agentes, estilos,
parámetros y almacenes para orquestar extracción, transformación y carga
de datos con trazabilidad y buenas prácticas.

---

## ¿Qué es Fragua?

Fragua ofrece una abstracción sobre tareas de integración de datos basada en tres agentes principales:

- **Extractor**: extrae datos desde distintas fuentes como Excel, CSV o APIs.
- **Transformer**: transforma o enriquece los datos aplicando reglas o modelos.
- **Loader**: guarda o entrega los resultados en destinos finales como archivos o bases de datos.

Incluye además un sistema de almacenamiento con:

- **Warehouse** y **WarehouseManager** para guardar artefactos intermedios con metadatos y trazabilidad.
- Arquitectura modular donde `styles`, `functions` y `params` pueden registrarse dentro de un `Environment`.

---

## Características principales

- Modelado de entornos (`Environment`) para aislar y organizar instancias de trabajo.
- Agentes (`Extractor`, `Transformer`, `Loader`) con pipeline común, capacidad de `undo` y registro de operaciones.
- Registries para `params`, `functions` y `styles`.
- Tipos de almacenamiento (`Storage`, `Box`, `Container`) y un `Warehouse` centralizado.
- Utilidades integradas para logging, métricas y resúmenes del estado de ejecución.

---

## Estructura del proyecto
```
fragua/
├── agents/
├── environments/
├── functions/
├── params/
├── styles/
├── storages/
├── utils/
└── __init__.py
```

---

## Instalación

Instala Fragua en modo editable desde la raíz del repositorio:
```bash 
python -m pip install -e .
```
Consulta `requirements.txt` para dependencias adicionales.

---



## Desarrollo

### Añadir un nuevo `style`

1. Crear una clase en `fragua/styles` que implemente el método `use`.
2. Crear los `Params` necesarios en `fragua/params`.
3. Registrar las clases en los registries o mediante la API del `Environment`.

### Añadir funciones reutilizables

Crear las funciones dentro de `fragua/functions` y registrarlas para su uso en la pipeline.

---

## Autor

**Santiago Lanz**  
📍 Desarrollador y creador de Fragua  
🌐 [Portfolio](https://sagodev.github.io/Portfolio-Web-Santiago-Lanz/)  
💼 [LinkedIn](https://www.linkedin.com/in/santiagolanz/)  
🐙 [GitHub](https://github.com/SagoDev)

---

## ⚖️ Licencia

Este proyecto se distribuye bajo la licencia **MIT**.  
Consulta el archivo `LICENSE` para más detalles.
