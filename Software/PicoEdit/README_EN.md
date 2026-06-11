# PicoEdit
<span><img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue"/></span>
<span><img src="https://img.shields.io/badge/PicoCalc-LuckFox%20%2B%20Linux-5E81AC?style=for-the-badge&logo=linux&logoColor=white"/></span>
<span><img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"/></span>
<span><img src="https://img.shields.io/badge/Ubuntu-24.04.2-E95420?style=for-the-badge&logo=ubuntu&logoColor=white"/></span>

* [Versión en español](https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/README.md)
* 
**PicoEdit** is a compact terminal-based code editor designed especially for small screens and portable devices such as the **Clockwork Pi PicoCalc**.

It was created as a simple, lightweight, self-contained tool for writing and testing Python scripts directly from a reduced-size terminal. Its goal is not to replace full-featured editors such as Vim, Nano, or VS Code, but to provide a practical, readable, and comfortable editing experience in an environment where every column and every line of screen space matters.

The editor is designed to work well on interfaces of approximately **53 columns by 26 rows**, with a sober visual style inspired by classic console tools.

<p align="center">
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/img/01.png" width="300"> 
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/img/05.png" width="300">
</p>

---

## Main features

* Plain-text editor focused on Python code.
* Syntax highlighting for Python.
* Recognition of keywords, functions, strings, numbers, and comments.
* Simple top menu with `File`, `Edit`, `Search`, `Run`, and `Help` sections.
* Built-in panel for opening `.py` files.
* Direct save and `Save as` support.
* Undo / Redo with a 10-level history.
* Copy, cut, paste, and duplicate lines.
* Text search and find next.
* Direct execution of the current Python script from inside the editor.
* Basic automatic indentation for Python blocks.
* Bottom status bar with current cursor position and editing mode.
* Fully English user interface.
* Implemented as a single file: `picoedit.py`.
* No external dependencies beyond standard Python and `curses`.

---

## Why PicoEdit?

On a desktop computer, there are many excellent options for editing code. But on a small screen, with a compact keyboard and limited resources, many of those tools can feel uncomfortable or excessive.

**PicoEdit** tries to fill that gap: a small, direct, and easy-to-use editor for writing short scripts, modifying configuration files, or testing Python ideas without leaving the terminal environment.

It is especially intended for projects where the PicoCalc is used as a tiny portable computer for experimenting with Linux and Python.

---

## Basic usage

PicoEdit can be launched directly from the terminal:

```bash
python3 picoedit.py
```

You can also open a specific file:

```bash
python3 picoedit.py my_script.py
```

If the file exists, it is loaded into the editor. If it does not exist, it can be created and saved from PicoEdit.

---

## Integrated use in another `curses` application

PicoEdit can also be used as a module inside another `curses`-based application.

```python
from apps.editor import picoedit

picoedit.ejecutar(stdscr, "my_script.py")
```

When used in this integrated mode, PicoEdit saves and restores the previous color palette, preventing it from altering the colors of the parent application after closing.

---

## Interface

The main screen is organized into three areas:

1. A top bar with the main menu.
2. The central editing area.
3. A bottom status bar.

The bottom bar shows:

```text
[ESC] Menu                         Ln 12 Col 8 INS
```

The `INS` indicator means the editor is in insert mode. If the editor is switched to replace mode, it shows `REP`.

<p align="center">
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/img/04.png" width="300"> 
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/img/03.png" width="300">
</p>

---

## Main menu

The top menu can be opened with:

```text
ESC
ALT + M
```

The menu is divided into sections:

```text
File   Edit   Search   Run   Help
```

From there, you can open files, save, run the script, access help, use Undo/Redo, and exit the editor.

To exit the editor, use:

```text
File > Exit
```

This avoids accidental exits when pressing `ESC`.

---

## Main shortcuts

Some shortcuts may depend on the behavior of each terminal or physical keyboard. For that reason, all important functions are also available from the menu.

### Menu

```text
ESC       Open menu
ALT + M   Open menu
```

### Files

```text
ALT + O   Open
ALT + S   Save
```

### Editing

```text
ALT + U   Undo
ALT + Y   Redo
ALT + C   Copy line
ALT + X   Cut line
ALT + V   Paste line
ALT + D   Duplicate line
```

### Search and execution

```text
ALT + F   Find
ALT + N   Find next
ALT + R   Run file
```

<p align="center">
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/Software/PicoEdit/img/02.png" width="300">
</p>

---

## Syntax highlighting

PicoEdit includes simple syntax highlighting for Python.

It currently distinguishes:

* Python reserved keywords.
* Built-in functions.
* Function calls.
* Strings.
* Numbers.
* Comments.
* Variables and identifiers.

The highlighting is designed to remain clear on small screens and terminals with limited color support.

---

## Undo / Redo

PicoEdit includes a simple Undo / Redo system with a 10-level history.

The history stores the text state, cursor position, horizontal and vertical scrolling, editing mode, and file modification state.

The history is reset when opening another file or creating a new file.

---

## Running the current script

From the `Run` menu, or through the corresponding shortcut, PicoEdit can execute the current Python file.

Before running, if there are unsaved changes, the editor asks whether the file should be saved.

During execution, PicoEdit temporarily suspends the `curses` interface, shows the program output in the terminal, and then lets you return to the editor by pressing `ENTER`.

---

## Opening files

PicoEdit includes a small file panel for navigating folders and opening `.py` scripts.

The panel lets you move through directories and select Python files without leaving the editor.

---

## Technical details

PicoEdit is written as a single Python file and uses only standard libraries.

Main components:

* `curses` for the terminal interface.
* `keyword` for detecting Python reserved keywords.
* `builtins` for recognizing built-in functions.
* `subprocess` for running the current script.
* `os` and `sys` for path handling, files, and execution.

The editor first tries to read files as `utf-8`. If that fails, it falls back to `latin-1`.

---

## Current limitations

PicoEdit is a small and experimental editor. Some design choices are constrained by screen size and by the behavior of compact terminals.

Known limitations:

* Syntax highlighting is simple and does not aim to cover every complex Python case.
* Some `ALT + key` combinations may depend on the terminal or keyboard being used.
* The file panel currently focuses on `.py` files.
* It is not intended for editing very large files.
* It is not meant to compete with full-featured editors, but to provide a practical tool for constrained environments.

---

## Possible future improvements

Ideas for future versions:

* Rename and delete files from the internal file panel.
* Improve handling of larger files.
* Extend syntax highlighting.
* Allow shortcut customization.
* Add basic support for other file types.
* Improve grouping of actions in Undo / Redo.

---

## Project status

PicoEdit is under active development. The current version is already functional for writing, editing, saving, and running Python scripts in a compact terminal, but it can still be improved.

The main focus of the project is to keep it simple, portable, and useful for PicoCalc users and other small Linux-based devices.
