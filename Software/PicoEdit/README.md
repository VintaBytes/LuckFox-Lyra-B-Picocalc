# PicoEdit
<span><img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue"/></span>
<span><img src="https://img.shields.io/badge/PicoCalc-LuckFox%20%2B%20Linux-5E81AC?style=for-the-badge&logo=linux&logoColor=white"/></span>
<span><img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"/></span>
<span><img src="https://img.shields.io/badge/Ubuntu-24.04.2-E95420?style=for-the-badge&logo=ubuntu&logoColor=white"/></span>


* [English version](https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/README_EN.md)

**PicoEdit** es un editor de código compacto para terminal, diseñado especialmente para pantallas pequeñas y dispositivos portátiles como la **Clockwork Pi PicoCalc**.

Nació como una herramienta simple, liviana y autocontenida para escribir y probar scripts de Python directamente desde una terminal de tamaño reducido. Su objetivo no es reemplazar a editores completos como Vim, Nano o VS Code, sino ofrecer una experiencia práctica, legible y cómoda en un entorno donde cada columna y cada línea de pantalla cuentan.

El editor está pensado para funcionar bien en interfaces de aproximadamente **53 columnas por 26 filas**, con una estética sobria inspirada en herramientas clásicas de consola.

<p align="center">
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/img/01.png" width="300"> 
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/img/05.png" width="300">
</p>

---

## Características principales

* Editor de texto plano orientado a código Python.
* Resaltado de sintaxis para Python.
* Reconocimiento de palabras reservadas, funciones, cadenas, números y comentarios.
* Menú superior simple con secciones `File`, `Edit`, `Search`, `Run` y `Help`.
* Panel interno para abrir archivos `.py`.
* Guardado directo y opción `Save as`.
* Undo / Redo con historial de 10 niveles.
* Copiar, cortar, pegar y duplicar líneas.
* Búsqueda de texto y búsqueda siguiente.
* Ejecución directa del script Python actual desde el editor.
* Indentación automática básica para bloques Python.
* Barra inferior con posición actual del cursor y modo de edición.
* Interfaz completamente en inglés.
* Implementado en un único archivo: `picoedit.py`.
* Sin dependencias externas más allá de Python estándar y `curses`.

---

## ¿Por qué PicoEdit?

En una computadora de escritorio hay muchas opciones excelentes para editar código. Pero en una pantalla pequeña, con teclado compacto y recursos limitados, muchas de esas herramientas pueden resultar incómodas o excesivas.

**PicoEdit** intenta cubrir ese espacio: un editor pequeño, directo y fácil de usar para escribir scripts breves, modificar archivos de configuración o probar ideas en Python sin salir del entorno de terminal.

Está pensado especialmente para proyectos donde la PicoCalc se usa como una pequeña computadora portátil para experimentar con Linux y Python.

---

## Uso básico

PicoEdit puede ejecutarse directamente desde la terminal:

```bash
python3 picoedit.py
```

También se puede abrir un archivo específico:

```bash
python3 picoedit.py mi_script.py
```

Si el archivo existe, se carga en el editor. Si no existe, se puede crear y guardar desde PicoEdit.

---

## Uso integrado en otra aplicación `curses`

PicoEdit también puede usarse como módulo dentro de otra aplicación basada en `curses`.

```python
from apps.editor import picoedit

picoedit.ejecutar(stdscr, "mi_script.py")
```

Cuando se usa integrado, PicoEdit guarda y restaura la paleta de colores previa, para evitar modificar los colores de la aplicación principal al cerrarse.

---

## Interfaz

La pantalla principal está organizada en tres zonas:

1. Una barra superior con el menú principal.
2. El área central de edición.
3. Una barra inferior con información de estado.

La barra inferior muestra:

```text
[ESC] Menu                         Ln 12 Col 8 INS
```

El indicador `INS` muestra que el editor está en modo inserción. Si se cambia a modo reemplazo, se muestra `REP`.

<p align="center">
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/img/04.png" width="300"> 
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/img/03.png" width="300">
</p>

---

## Menú principal

El menú superior se abre con:

```text
ESC
ALT + M
```

El menú está dividido en secciones:

```text
File   Edit   Search   Run   Help
```

Desde allí se pueden abrir archivos, guardar, ejecutar el script, acceder a ayuda, usar Undo/Redo y salir del editor.

La salida del editor se realiza desde:

```text
File > Exit
```

Esto evita cierres accidentales al presionar `ESC`.

---

## Atajos principales

Algunos atajos pueden depender del comportamiento de cada terminal o teclado físico. Por eso, todas las funciones importantes también están disponibles desde el menú.

### Menú

```text
ESC       Abrir menú
ALT + M   Abrir menú
```

### Archivos

```text
ALT + O   Open
ALT + S   Save
```

### Edición

```text
ALT + U   Undo
ALT + Y   Redo
ALT + C   Copy line
ALT + X   Cut line
ALT + V   Paste line
ALT + D   Duplicate line
```

### Búsqueda y ejecución

```text
ALT + F   Find
ALT + N   Find next
ALT + R   Run file
```
<p align="center">
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/img/02.png" width="300">
</p>

---

## Resaltado de sintaxis

PicoEdit incluye un resaltado de sintaxis simple para Python.

Actualmente distingue:

* Palabras reservadas de Python.
* Funciones incorporadas.
* Llamadas a funciones.
* Cadenas de texto.
* Números.
* Comentarios.
* Variables e identificadores.

El resaltado está diseñado para ser claro en pantallas pequeñas y terminales con soporte limitado de color.

---

## Undo / Redo

PicoEdit incorpora un sistema simple de Undo / Redo con un historial de 10 niveles.

El historial guarda el estado del texto, la posición del cursor, el desplazamiento horizontal y vertical, el modo de edición y el estado de modificación del archivo.

El historial se reinicia al abrir otro archivo o crear un archivo nuevo.

---

## Ejecución del script actual

Desde el menú `Run` o mediante el atajo correspondiente, PicoEdit puede ejecutar el archivo Python actual.

Antes de ejecutar, si hay cambios sin guardar, el editor pregunta si se desea guardar el archivo.

Durante la ejecución, PicoEdit suspende temporalmente la interfaz `curses`, muestra la salida del programa en la terminal y luego permite volver al editor presionando `ENTER`.

---

## Apertura de archivos

PicoEdit incluye un pequeño panel de archivos para navegar carpetas y abrir scripts `.py`.

El panel permite moverse entre directorios y seleccionar archivos de Python sin abandonar el editor.

---

## Detalles técnicos

PicoEdit está escrito como un único archivo Python y utiliza únicamente bibliotecas estándar.

Componentes principales:

* `curses` para la interfaz de terminal.
* `keyword` para detectar palabras reservadas de Python.
* `builtins` para reconocer funciones incorporadas.
* `subprocess` para ejecutar el script actual.
* `os` y `sys` para manejo de rutas, archivos y ejecución.

El editor intenta leer archivos primero como `utf-8`. Si eso falla, usa `latin-1` como alternativa.

---

## Limitaciones actuales

PicoEdit es un editor pequeño y experimental. Algunas decisiones están condicionadas por el tamaño de pantalla y por las particularidades de las terminales compactas.

Limitaciones conocidas:

* El resaltado de sintaxis es simple y no pretende cubrir todos los casos complejos de Python.
* Algunas combinaciones `ALT + tecla` pueden depender de la terminal o del teclado utilizado.
* El panel de archivos actualmente está enfocado en archivos `.py`.
* No está pensado para editar archivos muy grandes.
* No busca competir con editores completos, sino ofrecer una herramienta práctica para entornos reducidos.

---

## Posibles mejoras futuras

Algunas ideas para futuras versiones:

* Renombrar y borrar archivos desde el panel interno.
* Mejorar el manejo de archivos grandes.
* Ampliar el resaltado de sintaxis.
* Permitir personalizar atajos.
* Agregar soporte básico para otros tipos de archivo.
* Mejorar la agrupación de acciones en Undo / Redo.

---

## Estado del proyecto

PicoEdit está en desarrollo activo. La versión actual ya es funcional para escribir, editar, guardar y ejecutar scripts Python en una terminal compacta, pero todavía puede seguir mejorando.

El foco principal del proyecto es mantenerlo simple, portable y útil para usuarios de PicoCalc y otros dispositivos pequeños con Linux.
