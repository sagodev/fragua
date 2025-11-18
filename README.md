
# Fragua

**Fragua** es una biblioteca ligera y modular diseñada para construir pipelines ETL/ELT y flujos de procesamiento de datos en Python. Proporciona un conjunto de componentes reutilizables (entornos, agentes, estilos, parámetros y almacenes) para orquestar la extracción, transformación y carga de datos con trazabilidad y buenas prácticas.

---

## 🚀 ¿Qué es Fragua?

- Fragua ofrece una abstracción sobre tareas de integración de datos basada en tres roles principales (agentes):
  - Extractor: extrae datos desde distintas fuentes (por ejemplo Excel, CSV, APIs).
  - Transformer: transforma o enriquece los datos aplicando reglas o modelos.
  -  Loader: guarda o entrega los resultados en destinos finales (archivos, bases, servicios).
- Además Fragua integra un `Warehouse` (almacén) y un `WarehouseManager` para almacenar artefactos intermedios con metadatos y un log de movimientos.
- Es modular: los `styles`, `functions` y `params` se registran y reutilizan dentro de un `Environment`.

---

## 🔧 Características principales

- Modelado de entornos (`Environment`) para aislar y organizar instancias de trabajo.
- Agentes (`Extractor`, `Transformer`, `Loader`) con pipeline común, registro de operaciones y capacidad de `undo`.
- Registries para `params`, `functions` y `styles` que facilitan la extensión del sistema.
- Tipos de almacenamiento (`Storage`, `Box`, `Container`) y `Warehouse` para persistencia y trazabilidad.
- Utilidades para logging, métricas y resumen del estado de ejecución.

---

## 📁 Estructura del proyecto

La estructura principal del paquete es:

```
fragua/
├── agents/        # Extractor, Transformer, Loader, WarehouseManager
├── environments/  # Minimal and Basic Environment implementations
├── functions/     # Funciones reutilizables de extracción/transformación/
├── params/        # Clases Params para cada style
├── styles/        # Implementaciones de styles (excel, report, etc.)
├── storages/      # Warehouse, Storage base, tipos (Box, Container)
├── utils/         # Logger, metrics, summary, config
__ init__.py
```


---

## ⚙️ Instalación

Instala el paquete en modo editable desde la raíz del repo:

```powershell
python -m pip install -e .
```

Revisa `requirements.txt` para dependencias adicionales.

---

## 🚀 Ejemplo de uso

```python
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
transformer.work(style="report", apply_to="extracted_data", save_as="transformed_data")

# Cargar / exportar
loader.work(
    style="excel",
    apply_to=["extracted_data", "transformed_data"],
    destination="./test_files/output_files",
    file_name="output_file",
)

print(env.summary())
```

## 🛠️ Desarrollo

- Para añadir un nuevo `style` (por ejemplo un nuevo formato de extracción o carga):
  1. Añade una clase en `fragua/styles` que implemente la interfaz requerida (método `use`).
  2. Crea los `Params` en `fragua/params` si necesitas parámetros específicos.
  3. Registra las clases en las constantes de registro correspondientes o usa la API del `Environment` para registrar dinámicamente.

- Para añadir funciones reutilizables: crealas en `fragua/functions` y regístralos.

---

## 🧑‍💻 Autor

**Santiago Lanz**  
📍 Desarrollador y creador de Fragua  
🐙 [GitHub - SagoDev](https://github.com/SagoDev)

---

## ⚖️ Licencia

Este proyecto se publica bajo la licencia indicada en el archivo `LICENSE` en la raíz del repositorio.
