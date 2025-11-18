# Fragua

**Fragua** es una biblioteca ligera y modular diseñada para construir
pipelines ETL/ELT y flujos de procesamiento de datos en Python.
Proporciona componentes reutilizables (entornos, agentes, estilos,
parámetros y almacenes) para orquestar extracción, transformación y
carga de datos con trazabilidad y buenas prácticas.

------------------------------------------------------------------------

## 🚀 ¿Qué es Fragua?

Fragua ofrece una abstracción sobre tareas de integración de datos
basada en tres agentes principales:

-   **Extractor**: extrae datos desde distintas fuentes (Excel, CSV,
    APIs, etc.).
-   **Transformer**: transforma o enriquece los datos aplicando reglas o
    modelos.
-   **Loader**: carga o entrega los resultados en destinos finales
    (archivos, bases de datos, servicios).

También incluye un sistema de almacenamiento:

-   **Warehouse** y **WarehouseManager** para guardar artefactos
    intermedios con metadatos y trazabilidad.
-   Arquitectura modular donde `styles`, `functions` y `params` pueden
    registrarse dentro de un `Environment`.

------------------------------------------------------------------------

## 🔧 Características principales

-   Modelado de entornos (`Environment`) para aislar y organizar
    instancias de trabajo.
-   Agentes (`Extractor`, `Transformer`, `Loader`) con pipeline común,
    capacidad de `undo` y registro de operaciones.
-   Registries para `params`, `functions` y `styles`.
-   Múltiples tipos de almacenamiento (`Storage`, `Box`, `Container`) y
    un `Warehouse` centralizado.
-   Utilidades integradas para logging, métricas y resúmenes del estado
    de ejecución.

------------------------------------------------------------------------

## 📁 Estructura del proyecto

``` text
fragua/
├── agents/        # Extractor, Transformer, Loader, WarehouseManager
├── environments/  # Minimal and Basic Environment implementations
├── functions/     # Funciones reutilizables de extracción/transformación
├── params/        # Clases Params para cada style
├── styles/        # Implementaciones de styles (excel, report, etc.)
├── storages/      # Warehouse, Storage base, tipos (Box, Container)
├── utils/         # Logger, metrics, summary, config
└── __init__.py
```

------------------------------------------------------------------------

## ⚙️ Instalación

Instala Fragua en modo editable desde la raíz del repositorio:

``` bash
python -m pip install -e .
```

Consulta `requirements.txt` para dependencias adicionales.

------------------------------------------------------------------------

## 🚀 Ejemplo de uso

``` python
import fragua as fg

env = fg.create_fragua("fragua_1", "minimal", True)
env.create_extractor("extractor")
env.create_transformer("transformer")
env.create_loader("loader")

extractor = env.get_agent("extractor")
transformer = env.get_agent("transformer")
loader = env.get_agent("loader")

# Extraer desde Excel
extractor.work(
    "excel",
    save_as="extracted_data",
    path="./test_files/input_files/test_data.xlsx",
    sheet_name=0,
)

# Transformar
transformer.work(
    style="report",
    apply_to="extracted_data",
    save_as="transformed_data"
)

# Cargar / exportar
loader.work(
    style="excel",
    apply_to=["extracted_data", "transformed_data"],
    destination="./test_files/output_files",
    file_name="output_file",
)

print(env.summary())
```

------------------------------------------------------------------------

## 🛠️ Desarrollo

### Añadir un nuevo `style`

1.  Crear una clase en `fragua/styles` que implemente el método `use`.
2.  Añadir los `Params` necesarios en `fragua/params`.
3.  Registrar las clases en los registries o mediante la API del
    `Environment`.

### Añadir funciones reutilizables

-   Crear las funciones dentro de `fragua/functions` y registrarlas para
    su uso en la pipeline.

------------------------------------------------------------------------

## 🧑‍💻 Autor

**Santiago Lanz**\
📍 Desarrollador y creador de Fragua\
🐙 GitHub: https://github.com/SagoDev

------------------------------------------------------------------------

## ⚖️ Licencia

Publicado bajo la licencia detallada en el archivo `LICENSE` ubicado en
la raíz del repositorio.
