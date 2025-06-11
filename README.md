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

