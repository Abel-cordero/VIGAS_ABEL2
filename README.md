INSTRUCCIÓN PARA GENERAR UNA APLICACIÓN EN PYTHON – DISEÑO DE VIGAS SEGÚN NTP E.060 (PERÚ)
Objetivo del proyecto:

Crear una aplicación completa en Python con interfaz gráfica que permita:

Ingresar momentos flectores en 3 secciones de una viga (6 valores: + y − en cada punto)

Generar y mostrar diagramas de momentos originales y corregidos

Aplicar corrección de momentos automáticamente según el tipo de sistema estructural (dual 1 o 2), según Norma Técnica Peruana E.060

Pasar a una segunda ventana donde se haga el diseño de refuerzo:

Mostrar refuerzo requerido (superior)

Mostrar refuerzo diseñado (inferior)

Permitir manipular número y diámetro de varillas (hasta 2 tipos diferentes)

Verificar cumplimiento estructural según la norma

Exportar resultados en formato visual, incluyendo opción de captura automática para Word

ETAPA 1 – INTERFAZ PRINCIPAL: INGRESO Y DIAGRAMA DE MOMENTOS
Elementos requeridos:

Entrada de los 6 momentos:

M1+ y M1− (primer extremo)

M2+ y M2− (centro del vano)

M3+ y M3− (segundo extremo)

Selector de tipo de sistema:

Dual tipo 1

Dual tipo 2

Visualización:

Diagrama de momentos originales (sin corregir), representado gráficamente en la parte superior

Diagrama de momentos corregidos (según el sistema elegido), en la parte inferior

Cada diagrama debe tener etiquetas, unidades y leyenda

Botones:

“Calcular Momentos Corregidos” → genera el segundo diagrama con los valores corregidos

“Ir al Diseño de Acero” → cambia de interfaz a la segunda etapa del proceso

ETAPA 2 – INTERFAZ DE DISEÑO DE ACERO
Visualización principal:

Diagrama esquemático de la viga con refuerzos:

Parte superior: mostrar visualmente los aceros requeridos (según los momentos corregidos)

Parte inferior: mostrar visualmente los aceros de diseño seleccionados por el usuario

Elementos interactivos:

Selector para elegir hasta 2 tipos distintos de acero:

Casilla 1: cantidad y diámetro (ej. 2 Ø16)

Casilla 2: cantidad y diámetro (ej. 1 Ø25)

Cálculo automático del área de acero total de diseño

Comparación en pantalla:

Área requerida vs. área diseñada

Verificación de cumplimiento (diseño ≥ requerido)

Botones adicionales:

“Verificar diseño” → muestra si el diseño cumple o no

“Captura para Word” → toma automáticamente una captura de esta ventana y la guarda como imagen o la envía a Word (usar pyautogui y opcionalmente python-docx)

“Volver a Momentos” → para regresar a la etapa anterior y modificar datos si es necesario

CONSIDERACIONES TÉCNICAS:
Lenguaje: Python 3.x

Normativa: Toda lógica y cálculo se basa en la NTP E.060 (Perú). No es necesario explicar ni insertar fórmulas, ya que el modelo tiene acceso a ellas.

Librerías sugeridas:

tkinter (interfaz gráfica)

matplotlib (graficar los diagramas de momento)

pyautogui o Pillow (captura de pantalla)

python-docx (inserción opcional en Word)

math o numpy (cálculos)

El código debe estar modularizado:

Una función para corrección de momentos

Una función para cálculo de área de acero requerida

Una función para graficar momentos

Una función para comparar aceros

Una función para captura de interfaz

RESUMEN DE INTERFAZ (UX):
Ventana 1: Ingreso de momentos → Diagramas superior/inferior → Corrección → Botón "Ir al Diseño"

Ventana 2: Visualización de viga con aceros → Selección de varillas → Resultados y verificación → Botón captura/exportar

## Requisitos de plataforma

- Python 3.8 o superior instalado en el sistema.
- Sistema operativo con soporte para PyQt5 (Windows, macOS o distribuciones de
  Linux con entorno de escritorio).

## Instalación de dependencias

1. Se recomienda crear un entorno virtual con `venv` o herramienta similar.
2. Instalar las bibliotecas necesarias:

   ```bash
   pip install PyQt5 matplotlib numpy scipy mplcursors
   ```

   Para funciones opcionales de captura o exportación a Word se pueden agregar
   `pyautogui` y `python-docx`.

## Ejecución

Desde la raíz del repositorio ejecutar:

```bash
python viga2.0.py
```

Se abrirá la interfaz gráfica donde se ingresan los momentos y se generan los
diagramas correspondientes.


## Formulario de datos y flujos

La aplicación cuenta con dos ventanas principales:

**Ventana de Momentos**

- Seis campos numéricos (`QLineEdit`) para ingresar `M1-`, `M2-`, `M3-`, `M1+`, `M2+` y `M3+`.
- Selector del sistema estructural con dos opciones: `Dual 1` y `Dual 2`.
- Botones principales: **Calcular Diagramas**, **Ir a Diseño de Acero** y **Capturar Diagramas**.

**Ventana de Diseño**

- Parámetros de sección: `b`, `h`, `r`, `f'c`, `fy` y `φ`.
- Selección de diámetros de estribo y varilla mediante `QComboBox`.
- Combos de cantidad y diámetro para dos tipos de barra en cada posición de momento.
- Indicadores de `As` mínimo/máximo y base requerida.
- Botón **Capturar Diseño**.

Los diagramas y resultados se actualizan cada vez que se modifican los datos o se presionan los botones de cálculo.

## Estructura del código y objetos principales

Todo el código reside en `viga2.0.py`. A modo de referencia rápida se listan las clases y funciones más relevantes:

- **`MomentApp`**
  - `get_moments()` — lee los valores ingresados.
  - `correct_moments(mn, mp, sys_t)` — aplica la corrección de la NTP E.060.
  - `plot_original()` y `plot_corrected()` — generan los diagramas.
  - `on_calculate()` — coordina lectura y graficado.
  - `on_next()` — abre la ventana de diseño con los momentos corregidos.

- **`DesignWindow`**
  - `_calc_as_req()` y `_calc_as_limits()` — cálculos de acero requerido y límites.
  - `_required_areas()` — devuelve las áreas necesarias por posición.
  - `draw_section()`, `draw_required_distribution()` y `draw_design_distribution()` — funciones de representación gráfica.
  - `update_design_as()` — calcula el refuerzo propuesto y verifica la base.
  - `_capture_design()` — copia la vista al portapapeles.

Esta organización modular facilita la comunicación y coordinación dentro del equipo, ya que cada función se asocia a una tarea específica del flujo de trabajo.

