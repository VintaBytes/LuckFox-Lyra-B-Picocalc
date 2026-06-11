#!/usr/bin/env python3
# ------------------------------------------------------------
# PicoEdit
# Editor de texto compacto para terminal 53x22.
#
# Archivo autocontenido
#
# Uso:
#     python3 picoedit.py
#     python3 picoedit.py archivo.py
# ------------------------------------------------------------

import builtins
import curses
import keyword
import os
import subprocess
import sys


AN = 53
AL = 26

C_NORMAL = 1
C_TITULO = 2
C_RESALTA = 3
C_ERROR = 4
C_ESTADO = 5
C_RESULT = 6
C_DESTACA = 7
C_CARPETA = 8
C_KEYWORD = 9
C_NUMERO = 10
C_STRING = 11
C_COMENTARIO = 12
C_VARIABLE = 13
C_VENTANA = 14
C_VENTANA_BORDE = 15
C_VENTANA_SEL = 16
C_VENTANA_DIR = 17
C_VENTANA_ESTADO = 18
C_FUNCION = 19

ULTIMO_PAR_COLOR_EDITOR = 19

CTRL_C = 3
CTRL_D = 4
CTRL_F = 6
CTRL_G = 7
CTRL_N = 14
CTRL_O = 15
CTRL_R = 18
CTRL_S = 19
CTRL_V = 22
CTRL_X = 24

TECLA_ALT_MENU = ord("m")
TECLA_ALT_UNDO = ord("z")
TECLA_ALT_UNDO_ALT = ord("u")
TECLA_ALT_REDO = ord("y")
TECLA_ALT_COPY = ord("c")
TECLA_ALT_CUT = ord("x")
TECLA_ALT_PASTE = ord("v")
TECLA_ALT_DUP = ord("d")
TECLA_ALT_SAVE = ord("s")
TECLA_ALT_OPEN = ord("o")
TECLA_ALT_RUN = ord("r")
TECLA_ALT_FIND = ord("f")
TECLA_ALT_FIND_NEXT = ord("n")

MAX_UNDO = 10
ESPERA_ALT_MS = 40


PY_KEYWORDS = set(keyword.kwlist)
PY_BUILTINS = set(dir(builtins))

PALETA_ANTERIOR = {}


# ------------------------------------------------------------
# Guardado y restauracion de paleta de colores
# ------------------------------------------------------------
def guardar_paleta_actual():
    global PALETA_ANTERIOR

    PALETA_ANTERIOR = {}

    for par in range(1, ULTIMO_PAR_COLOR_EDITOR + 1):
        if par >= curses.COLOR_PAIRS:
            continue

        try:
            PALETA_ANTERIOR[par] = curses.pair_content(par)
        except curses.error:
            pass


def restaurar_paleta_anterior():
    if not PALETA_ANTERIOR:
        return

    for par, colores in PALETA_ANTERIOR.items():
        if par >= curses.COLOR_PAIRS:
            continue

        try:
            fg, bg = colores
            curses.init_pair(par, fg, bg)
        except curses.error:
            pass


# ------------------------------------------------------------
# Inicializacion de curses
# ------------------------------------------------------------
def iniciar_curses(stdscr):
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(False)

    curses.start_color()
    curses.use_default_colors()
    guardar_paleta_actual()

    # Editor principal
    curses.init_pair(C_NORMAL, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(C_TITULO, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(C_RESALTA, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(C_ERROR, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(C_ESTADO, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(C_RESULT, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(C_DESTACA, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(C_CARPETA, curses.COLOR_CYAN, curses.COLOR_BLUE)

    # Sintaxis Python.
    curses.init_pair(C_KEYWORD, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(C_NUMERO, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(C_STRING, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(C_COMENTARIO, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(C_VARIABLE, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(C_FUNCION, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # Ventanas flotantes
    curses.init_pair(C_VENTANA, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(C_VENTANA_BORDE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(C_VENTANA_SEL, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(C_VENTANA_DIR, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(C_VENTANA_ESTADO, curses.COLOR_YELLOW, curses.COLOR_BLACK)


# ------------------------------------------------------------
# Primitivas de pantalla
# ------------------------------------------------------------
def escribir(stdscr, x, y, texto, color=C_NORMAL):
    if y < 0 or y >= AL:
        return
    if x < 0 or x >= AN:
        return

    try:
        stdscr.addstr(y, x, str(texto)[:AN - x], curses.color_pair(color))
    except curses.error:
        pass


def escribir_color(stdscr, x, y, char, color=C_NORMAL):
    if y < 0 or y >= AL:
        return
    if x < 0 or x >= AN:
        return

    try:
        attr = curses.color_pair(color)

        if color == C_COMENTARIO:
            attr = attr | curses.A_DIM

        stdscr.addstr(y, x, char, attr)
    except curses.error:
        pass


def escribir_attr(stdscr, x, y, texto, color=C_NORMAL, attr=0):
    if y < 0 or y >= AL:
        return
    if x < 0 or x >= AN:
        return

    try:
        stdscr.addstr(y, x, str(texto)[:AN - x], curses.color_pair(color) | attr)
    except curses.error:
        pass


def limpiar_area(stdscr):
    for y in range(AL):
        escribir(stdscr, 0, y, " " * AN, C_NORMAL)


def linea_h(stdscr, y):
    escribir(stdscr, 0, y, "─" * AN, C_TITULO)


def normalizar_ruta(ruta):
    if not ruta:
        return None
    return os.path.abspath(os.path.expanduser(ruta))


# ------------------------------------------------------------
# Entrada para uso integrado
# ------------------------------------------------------------
def ejecutar(stdscr, ruta_archivo=None):
    iniciar_curses(stdscr)

    try:
        editor = PicoEdit(stdscr, ruta_archivo)
        editor.bucle()
    finally:
        restaurar_paleta_anterior()
        stdscr.refresh()


class PicoEdit:
    def __init__(self, stdscr, ruta_archivo=None):
        self.stdscr = stdscr
        self.ruta_archivo = normalizar_ruta(ruta_archivo)
        self.carpeta_actual = os.getcwd()

        if self.ruta_archivo:
            self.carpeta_actual = os.path.dirname(self.ruta_archivo) or os.getcwd()

        self.lineas = []
        self.cursor_fila = 0
        self.cursor_col = 0
        self.offset_fila = 0
        self.offset_col = 0

        self.modificado = False
        self.insertar = True
        self.portapapeles = ""
        self.busqueda = ""
        self.mensaje = ""

        self.undo_stack = []
        self.redo_stack = []

        if self.ruta_archivo:
            self.cargar_archivo()
        else:
            self.lineas = [""]

        if not self.lineas:
            self.lineas = [""]

    # ------------------------------------------------------------
    # Propiedades auxiliares
    # ------------------------------------------------------------
    def nombre_archivo(self):
        if self.ruta_archivo:
            return os.path.basename(self.ruta_archivo)
        return "new"

    def ruta_para_guardar_defecto(self):
        if self.ruta_archivo:
            return os.path.basename(self.ruta_archivo)
        return ""

    # ------------------------------------------------------------
    # Carga y guardado
    # ------------------------------------------------------------
    def cargar_archivo(self):
        if not self.ruta_archivo or not os.path.exists(self.ruta_archivo):
            self.lineas = [""]
            return

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                self.lineas = f.read().splitlines()
        except UnicodeDecodeError:
            with open(self.ruta_archivo, "r", encoding="latin-1") as f:
                self.lineas = f.read().splitlines()
        except Exception as e:
            self.lineas = [f"Error opening file: {e}"]

    def guardar_archivo_directo(self):
        if not self.ruta_archivo:
            return self.guardar_como()

        try:
            carpeta = os.path.dirname(self.ruta_archivo)
            if carpeta:
                os.makedirs(carpeta, exist_ok=True)

            with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                for i, linea in enumerate(self.lineas):
                    f.write(linea)
                    if i < len(self.lineas) - 1:
                        f.write("\n")

            self.modificado = False
            self.mensaje = "Saved."
            return True
        except Exception as e:
            self.mensaje = f"Error: {e}"
            return False

    def guardar_archivo(self):
        if self.ruta_archivo:
            return self.guardar_archivo_directo()

        return self.guardar_como()

    def guardar_como(self):
        inicial = self.ruta_para_guardar_defecto()

        nombre = self.input_barra("Save as: ", inicial)

        if nombre is None:
            self.mensaje = "Save canceled."
            return False

        nombre = nombre.strip()

        if not nombre:
            self.mensaje = "Empty filename."
            return False

        if os.path.isabs(nombre):
            ruta = normalizar_ruta(nombre)
        else:
            ruta = normalizar_ruta(os.path.join(self.carpeta_actual, nombre))

        if os.path.exists(ruta):
            if not self.confirmar_simple(f"Overwrite {os.path.basename(ruta)}? Y/N"):
                self.mensaje = "Not overwritten."
                return False

        ruta_anterior = self.ruta_archivo
        carpeta_anterior = self.carpeta_actual

        self.ruta_archivo = ruta
        self.carpeta_actual = os.path.dirname(ruta) or self.carpeta_actual

        if self.guardar_archivo_directo():
            return True

        self.ruta_archivo = ruta_anterior
        self.carpeta_actual = carpeta_anterior
        return False

    # ------------------------------------------------------------
    # Geometria de pantalla
    # ------------------------------------------------------------
    def area_texto(self):
        y_ini = 1
        y_fin = AL - 2
        alto = y_fin - y_ini + 1
        return y_ini, y_fin, alto

    # ------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------
    def dibujar(self):
        limpiar_area(self.stdscr)
        self.dibujar_barra_superior()
        self.dibujar_texto()
        self.dibujar_barra_inferior()
        self.asegurar_cursor_visible()
        self.posicionar_cursor()
        self.stdscr.refresh()

    def dibujar_barra_superior(self):
        marca = "*" if self.modificado else " "
        nombre = self.nombre_archivo()
        menu = " File  Edit  Search  Run  Help "
        info = f"{marca} {nombre}"

        libre = AN - len(menu) - len(info)

        if libre < 1:
            titulo = menu[:AN]
        else:
            titulo = menu + " " * libre + info

        escribir(self.stdscr, 0, 0, titulo[:AN].ljust(AN), C_TITULO)

    def dibujar_barra_inferior(self):
        modo = "INS" if self.insertar else "REP"
        estado = f"Ln {self.cursor_fila + 1} Col {self.cursor_col + 1} {modo}"
        izquierda = "[ESC] Menu"

        escribir(self.stdscr, 0, AL - 1, " " * AN, C_TITULO)
        escribir(self.stdscr, 0, AL - 1, izquierda[:AN], C_TITULO)

        x_estado = max(0, AN - len(estado))
        escribir(self.stdscr, x_estado, AL - 1, estado[:AN], C_TITULO)


    def dibujar_texto(self):
        y_ini, y_fin, alto = self.area_texto()

        for y in range(y_ini, y_fin + 1):
            escribir(self.stdscr, 0, y, " " * AN, C_NORMAL)

        fin = min(len(self.lineas), self.offset_fila + alto)

        for i in range(self.offset_fila, fin):
            y = y_ini + (i - self.offset_fila)
            linea = self.lineas[i]
            self.dibujar_linea_codigo(y, linea)

    def dibujar_linea_codigo(self, y, linea):
        estilos = self.estilos_sintaxis(linea)

        frag = linea[self.offset_col:self.offset_col + AN]
        estilos_frag = estilos[self.offset_col:self.offset_col + AN]

        if self.offset_col > 0 and AN > 1:
            if frag:
                frag = "←" + frag[1:]
                estilos_frag = [C_ESTADO] + estilos_frag[1:]
            else:
                frag = "←"
                estilos_frag = [C_ESTADO]

        if len(linea) > self.offset_col + AN and AN > 1:
            if len(frag) >= AN:
                frag = frag[:AN - 1] + "→"
                estilos_frag = estilos_frag[:AN - 1] + [C_ESTADO]
            else:
                frag += "→"
                estilos_frag.append(C_ESTADO)

        frag = frag[:AN]
        estilos_frag = estilos_frag[:AN]

        for x, ch in enumerate(frag):
            color_ch = estilos_frag[x] if x < len(estilos_frag) else C_NORMAL
            escribir_color(self.stdscr, x, y, ch, color_ch)

    def es_llamada_funcion(self, linea, pos):
        i = pos
        n = len(linea)

        while i < n and linea[i].isspace():
            i += 1

        return i < n and linea[i] == "("

    def estilos_sintaxis(self, linea):
        estilos = [C_NORMAL for _ in linea]
        n = len(linea)
        i = 0

        while i < n:
            ch = linea[i]

            if ch == "#":
                for j in range(i, n):
                    estilos[j] = C_COMENTARIO
                break

            if ch in ("'", '"'):
                quote = ch
                inicio = i
                triple = i + 2 < n and linea[i:i + 3] == quote * 3

                if triple:
                    i += 3
                    while i < n:
                        if i + 2 < n and linea[i:i + 3] == quote * 3:
                            i += 3
                            break
                        i += 1
                else:
                    i += 1
                    escape = False
                    while i < n:
                        if escape:
                            escape = False
                        elif linea[i] == "\\":
                            escape = True
                        elif linea[i] == quote:
                            i += 1
                            break
                        i += 1

                for j in range(inicio, min(i, n)):
                    estilos[j] = C_STRING
                continue

            if ch.isdigit() or (
                ch == "."
                and i + 1 < n
                and linea[i + 1].isdigit()
            ):
                inicio = i
                i += 1

                while i < n and (
                    linea[i].isdigit()
                    or linea[i] in ".xXabcdefABCDEF_"
                    or linea[i] in "eEjJ+-"
                ):
                    if linea[i] in "+-" and linea[i - 1] not in "eE":
                        break
                    i += 1

                for j in range(inicio, min(i, n)):
                    estilos[j] = C_NUMERO
                continue

            if ch.isalpha() or ch == "_":
                inicio = i
                i += 1

                while i < n and (linea[i].isalnum() or linea[i] == "_"):
                    i += 1

                palabra = linea[inicio:i]

                if palabra in PY_KEYWORDS:
                    color_palabra = C_KEYWORD
                elif palabra in PY_BUILTINS or self.es_llamada_funcion(linea, i):
                    color_palabra = C_FUNCION
                else:
                    color_palabra = C_VARIABLE

                for j in range(inicio, i):
                    estilos[j] = color_palabra

                continue

            i += 1

        return estilos

    def asegurar_cursor_visible(self):
        _, _, alto = self.area_texto()

        if self.cursor_fila < self.offset_fila:
            self.offset_fila = self.cursor_fila
        elif self.cursor_fila >= self.offset_fila + alto:
            self.offset_fila = self.cursor_fila - alto + 1

        if self.cursor_col < self.offset_col:
            self.offset_col = self.cursor_col
        elif self.cursor_col >= self.offset_col + AN:
            self.offset_col = self.cursor_col - AN + 1

        self.offset_fila = max(0, self.offset_fila)
        self.offset_col = max(0, self.offset_col)

    def posicionar_cursor(self):
        y_ini, y_fin, _ = self.area_texto()
        y = y_ini + (self.cursor_fila - self.offset_fila)
        x = self.cursor_col - self.offset_col

        y = max(y_ini, min(y, y_fin))
        x = max(0, min(x, AN - 1))

        try:
            self.stdscr.move(y, x)
        except curses.error:
            pass

    # ------------------------------------------------------------
    # Bucle principal
    # ------------------------------------------------------------
    def bucle(self):
        curses.curs_set(1)

        while True:
            self.dibujar()
            tecla = self.leer_tecla_principal()
            self.mensaje = ""

            if tecla == "menu":
                accion = self.menu_superior()

                if accion == "salir":
                    break
            elif tecla == "undo":
                self.deshacer()
            elif tecla == "redo":
                self.rehacer()
            elif tecla == "copy":
                self.copiar_linea()
            elif tecla == "cut":
                self.cortar_linea()
            elif tecla == "paste":
                self.pegar_linea()
            elif tecla == "duplicate":
                self.duplicar_linea()
            elif tecla == "save":
                self.guardar_archivo()
            elif tecla == "open":
                self.abrir_desde_panel()
            elif tecla == "run":
                self.ejecutar_programa()
            elif tecla == "find":
                self.buscar()
            elif tecla == "find_next":
                self.buscar_siguiente()
            elif tecla == curses.KEY_F1 or tecla == CTRL_G:
                self.mostrar_ayuda()
            elif tecla == curses.KEY_F2 or tecla == CTRL_S:
                self.guardar_archivo()
            elif tecla == curses.KEY_F3 or tecla == CTRL_F:
                self.buscar()
            elif tecla == curses.KEY_F4 or tecla == CTRL_N:
                self.buscar_siguiente()
            elif tecla == curses.KEY_F5 or tecla == curses.KEY_IC:
                self.insertar = not self.insertar
            elif tecla == curses.KEY_F6 or tecla == CTRL_O:
                self.abrir_desde_panel()
            elif tecla == curses.KEY_F7:
                self.guardar_como()
            elif tecla == curses.KEY_F8 or tecla == CTRL_R:
                self.ejecutar_programa()
            elif tecla == 27:
                accion = self.menu_superior()

                if accion == "salir":
                    break
            else:
                self.manejar_tecla_edicion(tecla)

        curses.curs_set(0)
        limpiar_area(self.stdscr)
        self.stdscr.refresh()

    # ------------------------------------------------------------
    # Undo / Redo
    # ------------------------------------------------------------
    def crear_estado_editor(self):
        return {
            "lineas": list(self.lineas),
            "cursor_fila": self.cursor_fila,
            "cursor_col": self.cursor_col,
            "offset_fila": self.offset_fila,
            "offset_col": self.offset_col,
            "modificado": self.modificado,
            "insertar": self.insertar,
        }

    def restaurar_estado_editor(self, estado):
        self.lineas = list(estado["lineas"])

        if not self.lineas:
            self.lineas = [""]

        self.cursor_fila = max(0, min(estado["cursor_fila"], len(self.lineas) - 1))
        self.cursor_col = max(0, min(estado["cursor_col"], len(self.lineas[self.cursor_fila])))

        self.offset_fila = max(0, estado["offset_fila"])
        self.offset_col = max(0, estado["offset_col"])
        self.modificado = estado["modificado"]
        self.insertar = estado["insertar"]

    def guardar_undo(self):
        estado = self.crear_estado_editor()

        if self.undo_stack and self.undo_stack[-1] == estado:
            return

        self.undo_stack.append(estado)

        if len(self.undo_stack) > MAX_UNDO:
            self.undo_stack.pop(0)

        self.redo_stack.clear()

    def limpiar_undo_redo(self):
        self.undo_stack.clear()
        self.redo_stack.clear()

    def deshacer(self):
        if not self.undo_stack:
            self.mensaje = "Nothing to undo."
            return None

        estado_actual = self.crear_estado_editor()
        estado_anterior = self.undo_stack.pop()

        self.redo_stack.append(estado_actual)

        if len(self.redo_stack) > MAX_UNDO:
            self.redo_stack.pop(0)

        self.restaurar_estado_editor(estado_anterior)
        self.mensaje = "Undo."

        return None

    def rehacer(self):
        if not self.redo_stack:
            self.mensaje = "Nothing to redo."
            return None

        estado_actual = self.crear_estado_editor()
        estado_siguiente = self.redo_stack.pop()

        self.undo_stack.append(estado_actual)

        if len(self.undo_stack) > MAX_UNDO:
            self.undo_stack.pop(0)

        self.restaurar_estado_editor(estado_siguiente)
        self.mensaje = "Redo."

        return None


    # ------------------------------------------------------------
    # Menu superior
    # ------------------------------------------------------------
    def leer_tecla_principal(self):
        tecla = self.stdscr.getch()

        if tecla != 27:
            return tecla

        # ALT+letra suele llegar como ESC seguido de una letra.
        # Esperamos muy poco para distinguirlo de ESC solo.
        self.stdscr.timeout(ESPERA_ALT_MS)

        try:
            siguiente = self.stdscr.getch()
        finally:
            self.stdscr.timeout(-1)

        mapa_alt = {
            TECLA_ALT_MENU: "menu",
            ord("M"): "menu",
            TECLA_ALT_UNDO: "undo",
            ord("Z"): "undo",
            TECLA_ALT_UNDO_ALT: "undo",
            ord("U"): "undo",
            TECLA_ALT_REDO: "redo",
            ord("Y"): "redo",
            TECLA_ALT_COPY: "copy",
            ord("C"): "copy",
            TECLA_ALT_CUT: "cut",
            ord("X"): "cut",
            TECLA_ALT_PASTE: "paste",
            ord("V"): "paste",
            TECLA_ALT_DUP: "duplicate",
            ord("D"): "duplicate",
            TECLA_ALT_SAVE: "save",
            ord("S"): "save",
            TECLA_ALT_OPEN: "open",
            ord("O"): "open",
            TECLA_ALT_RUN: "run",
            ord("R"): "run",
            TECLA_ALT_FIND: "find",
            ord("F"): "find",
            TECLA_ALT_FIND_NEXT: "find_next",
            ord("N"): "find_next",
        }

        if siguiente in mapa_alt:
            return mapa_alt[siguiente]

        if siguiente != -1:
            curses.ungetch(siguiente)

        return 27


    def opciones_menu_superior(self):
        return [
            {
                "titulo": "File",
                "x": 1,
                "opciones": [
                    ("New", self.nuevo_archivo),
                    ("Open", self.abrir_desde_panel),
                    ("Save", self.guardar_archivo),
                    ("Save as", self.guardar_como),
                    ("Exit", self.salir_desde_menu),
                ],
            },
            {
                "titulo": "Edit",
                "x": 7,
                "opciones": [
                    ("Undo", self.deshacer),
                    ("Redo", self.rehacer),
                    ("Cut line", self.cortar_linea),
                    ("Copy line", self.copiar_linea),
                    ("Paste line", self.pegar_linea),
                    ("Duplicate", self.duplicar_linea),
                    ("Ins/Rep", self.alternar_insertar),
                ],
            },
            {
                "titulo": "Search",
                "x": 13,
                "opciones": [
                    ("Find", self.buscar),
                    ("Find next", self.buscar_siguiente),
                ],
            },
            {
                "titulo": "Run",
                "x": 21,
                "opciones": [
                    ("Run file", self.ejecutar_programa),
                ],
            },
            {
                "titulo": "Help",
                "x": 26,
                "opciones": [
                    ("Help", self.mostrar_ayuda),
                    ("About", self.mostrar_acerca_de),
                ],
            },
        ]

    def menu_superior(self):
        menus = self.opciones_menu_superior()
        menu_sel = 0
        item_sel = 0

        curses.curs_set(0)

        while True:
            self.dibujar()
            self.dibujar_menu_superior(menus, menu_sel, item_sel)
            self.stdscr.refresh()

            tecla = self.stdscr.getch()

            if tecla == 27:
                curses.curs_set(1)
                return None

            if tecla == curses.KEY_LEFT:
                menu_sel = (menu_sel - 1) % len(menus)
                item_sel = 0
                continue

            if tecla == curses.KEY_RIGHT:
                menu_sel = (menu_sel + 1) % len(menus)
                item_sel = 0
                continue

            opciones = menus[menu_sel]["opciones"]

            if tecla == curses.KEY_UP:
                item_sel = (item_sel - 1) % len(opciones)
                continue

            if tecla == curses.KEY_DOWN:
                item_sel = (item_sel + 1) % len(opciones)
                continue

            if tecla in (10, 13, curses.KEY_ENTER):
                funcion = opciones[item_sel][1]
                resultado = funcion()
                curses.curs_set(1)
                return resultado

            if 32 <= tecla <= 126:
                letra = chr(tecla).lower()

                for i, (nombre, funcion) in enumerate(opciones):
                    if nombre and nombre[0].lower() == letra:
                        item_sel = i
                        resultado = funcion()
                        curses.curs_set(1)
                        return resultado

    def dibujar_menu_superior(self, menus, menu_sel, item_sel):
        menu = menus[menu_sel]

        for i, dato in enumerate(menus):
            color = C_RESALTA if i == menu_sel else C_TITULO
            escribir(
                self.stdscr,
                dato["x"],
                0,
                " " + dato["titulo"] + " ",
                color
            )

        ancho = max(len(nombre) for nombre, _ in menu["opciones"]) + 4
        alto = len(menu["opciones"]) + 2
        x = menu["x"]
        y = 1

        if x + ancho >= AN:
            x = AN - ancho - 1

        self.dibujar_ventana(x, y, ancho, alto, menu["titulo"])

        for i, (nombre, _) in enumerate(menu["opciones"]):
            color = C_VENTANA_SEL if i == item_sel else C_VENTANA
            self.escribir_en_ventana(
                x + 2,
                y + 1 + i,
                ancho - 4,
                nombre,
                color
            )

    def nuevo_archivo(self):
        if self.modificado:
            r = self.confirmar_tres_opciones("Unsaved changes. Save first? Y/N/ESC")

            if r == "esc":
                return None

            if r == "y":
                if not self.guardar_archivo():
                    return None

        self.ruta_archivo = None
        self.lineas = [""]
        self.cursor_fila = 0
        self.cursor_col = 0
        self.offset_fila = 0
        self.offset_col = 0
        self.modificado = False
        self.limpiar_undo_redo()
        self.mensaje = "New file."

        return None

    def alternar_insertar(self):
        self.insertar = not self.insertar
        return None

    def salir_desde_menu(self):
        if self.confirmar_salida():
            return "salir"

        return None

    def mostrar_acerca_de(self):
        lineas = [
            "PicoEdit",
            "",
            "Compact editor for PicoCalc Linux.",
            "",
            "ALT+M opens the top menu.",
            "Exit is located under File > Exit.",
            "",
            "Ariel Palazzesi 2026",
        ]

        ancho = 43
        alto = 10
        x = (AN - ancho) // 2
        y = (AL - alto) // 2

        self.dibujar()
        self.dibujar_ventana(x, y, ancho, alto, "About")

        for i, linea in enumerate(lineas):
            self.escribir_en_ventana(x + 2, y + 2 + i, ancho - 4, linea, C_VENTANA)

        self.stdscr.refresh()

        while True:
            tecla = self.stdscr.getch()

            if tecla in (27, 10, 13, curses.KEY_ENTER):
                return None


    # ------------------------------------------------------------
    # Edicion
    # ------------------------------------------------------------
    def manejar_tecla_edicion(self, tecla):
        if tecla == curses.KEY_UP:
            self.mover_arriba()
        elif tecla == curses.KEY_DOWN:
            self.mover_abajo()
        elif tecla == curses.KEY_LEFT:
            self.mover_izquierda()
        elif tecla == curses.KEY_RIGHT:
            self.mover_derecha()
        elif tecla == curses.KEY_HOME:
            self.cursor_col = 0
        elif tecla == curses.KEY_END:
            self.cursor_col = len(self.lineas[self.cursor_fila])
        elif tecla == curses.KEY_PPAGE:
            self.page_up()
        elif tecla == curses.KEY_NPAGE:
            self.page_down()
        elif tecla in (curses.KEY_BACKSPACE, 127, 8):
            self.backspace()
        elif tecla == curses.KEY_DC:
            self.delete()
        elif tecla in (10, 13, curses.KEY_ENTER):
            self.insertar_salto_linea()
        elif tecla == 9:
            self.insertar_texto("    ")
        elif tecla == CTRL_X:
            self.cortar_linea()
        elif tecla == CTRL_C:
            self.copiar_linea()
        elif tecla == CTRL_V:
            self.pegar_linea()
        elif tecla == CTRL_D:
            self.duplicar_linea()
        elif 32 <= tecla <= 126:
            self.insertar_texto(chr(tecla))

    def mover_arriba(self):
        if self.cursor_fila > 0:
            self.cursor_fila -= 1
            self.ajustar_columna()

    def mover_abajo(self):
        if self.cursor_fila < len(self.lineas) - 1:
            self.cursor_fila += 1
            self.ajustar_columna()

    def mover_izquierda(self):
        if self.cursor_col > 0:
            self.cursor_col -= 1
        elif self.cursor_fila > 0:
            self.cursor_fila -= 1
            self.cursor_col = len(self.lineas[self.cursor_fila])

    def mover_derecha(self):
        if self.cursor_col < len(self.lineas[self.cursor_fila]):
            self.cursor_col += 1
        elif self.cursor_fila < len(self.lineas) - 1:
            self.cursor_fila += 1
            self.cursor_col = 0

    def page_up(self):
        _, _, alto = self.area_texto()
        self.cursor_fila = max(0, self.cursor_fila - alto)
        self.ajustar_columna()

    def page_down(self):
        _, _, alto = self.area_texto()
        self.cursor_fila = min(len(self.lineas) - 1, self.cursor_fila + alto)
        self.ajustar_columna()

    def ajustar_columna(self):
        self.cursor_col = min(self.cursor_col, len(self.lineas[self.cursor_fila]))

    def insertar_texto(self, texto):
        self.guardar_undo()

        for ch in texto:
            linea = self.lineas[self.cursor_fila]

            if self.insertar or self.cursor_col >= len(linea):
                self.lineas[self.cursor_fila] = linea[:self.cursor_col] + ch + linea[self.cursor_col:]
            else:
                self.lineas[self.cursor_fila] = linea[:self.cursor_col] + ch + linea[self.cursor_col + 1:]

            self.cursor_col += 1

        self.modificado = True

    def insertar_salto_linea(self):
        self.guardar_undo()

        linea = self.lineas[self.cursor_fila]
        izquierda = linea[:self.cursor_col]
        derecha = linea[self.cursor_col:]

        self.lineas[self.cursor_fila] = izquierda

        indent = ""
        for ch in izquierda:
            if ch in (" ", "\t"):
                indent += ch
            else:
                break

        if self.nombre_archivo().endswith(".py") and izquierda.strip().endswith(":"):
            indent += "    "

        self.lineas.insert(self.cursor_fila + 1, indent + derecha)
        self.cursor_fila += 1
        self.cursor_col = len(indent)
        self.modificado = True

    def backspace(self):
        if self.cursor_col > 0:
            self.guardar_undo()
            linea = self.lineas[self.cursor_fila]
            self.lineas[self.cursor_fila] = linea[:self.cursor_col - 1] + linea[self.cursor_col:]
            self.cursor_col -= 1
            self.modificado = True
            return

        if self.cursor_fila > 0:
            self.guardar_undo()
            actual = self.lineas[self.cursor_fila]
            anterior = self.lineas[self.cursor_fila - 1]
            self.cursor_col = len(anterior)
            self.lineas[self.cursor_fila - 1] = anterior + actual
            del self.lineas[self.cursor_fila]
            self.cursor_fila -= 1
            self.modificado = True

    def delete(self):
        linea = self.lineas[self.cursor_fila]

        if self.cursor_col < len(linea):
            self.guardar_undo()
            self.lineas[self.cursor_fila] = linea[:self.cursor_col] + linea[self.cursor_col + 1:]
            self.modificado = True
            return

        if self.cursor_fila < len(self.lineas) - 1:
            self.guardar_undo()
            self.lineas[self.cursor_fila] += self.lineas[self.cursor_fila + 1]
            del self.lineas[self.cursor_fila + 1]
            self.modificado = True

    def copiar_linea(self):
        self.portapapeles = self.lineas[self.cursor_fila]
        self.mensaje = "Line copied."

    def cortar_linea(self):
        self.guardar_undo()

        self.portapapeles = self.lineas[self.cursor_fila]

        if len(self.lineas) == 1:
            self.lineas[0] = ""
            self.cursor_col = 0
        else:
            del self.lineas[self.cursor_fila]
            self.cursor_fila = min(self.cursor_fila, len(self.lineas) - 1)
            self.ajustar_columna()

        self.modificado = True
        self.mensaje = "Line cut."

    def pegar_linea(self):
        self.guardar_undo()

        self.lineas.insert(self.cursor_fila + 1, self.portapapeles)
        self.cursor_fila += 1
        self.cursor_col = len(self.portapapeles)
        self.modificado = True
        self.mensaje = "Line pasted."

    def duplicar_linea(self):
        self.guardar_undo()

        linea = self.lineas[self.cursor_fila]
        self.lineas.insert(self.cursor_fila + 1, linea)
        self.cursor_fila += 1
        self.cursor_col = min(self.cursor_col, len(linea))
        self.modificado = True
        self.mensaje = "Line duplicated."

    # ------------------------------------------------------------
    # Ejecutar el programa actual
    # ------------------------------------------------------------
    def ejecutar_programa(self):
        if not self.ruta_archivo:
            self.mensaje = "Save the file before running."
            if not self.guardar_como():
                return

        if self.modificado:
            r = self.confirmar_tres_opciones("Save before running? Y/N/ESC")

            if r == "esc":
                self.mensaje = "Execution canceled."
                return

            if r == "y":
                if not self.guardar_archivo_directo():
                    return

        if not self.ruta_archivo:
            self.mensaje = "No file to run."
            return

        if not self.ruta_archivo.endswith(".py"):
            if not self.confirmar_simple("Not a .py file. Run anyway? Y/N"):
                return

        carpeta = os.path.dirname(self.ruta_archivo) or os.getcwd()

        curses.def_prog_mode()
        curses.endwin()

        try:
            print()
            print("Running:", self.ruta_archivo)
            print("-----------------------------------------------------")
            resultado = subprocess.run(
                [sys.executable, self.ruta_archivo],
                cwd=carpeta,
                check=False
            )
            print("-----------------------------------------------------")
            print(f"Process finished. Code: {resultado.returncode}")
            input("Press ENTER to return to PicoEdit...")
        except Exception as e:
            print()
            print("Error while running:")
            print(e)
            input("Press ENTER to return to PicoEdit...")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(1)
            self.mensaje = "Execution finished."
            self.stdscr.refresh()


    # ------------------------------------------------------------
    # Busqueda
    # ------------------------------------------------------------
    def buscar(self):
        termino = self.input_barra("Search: ", self.busqueda)

        if termino is None:
            return

        self.busqueda = termino
        self.buscar_siguiente(desde_inicio=True)

    def buscar_siguiente(self, desde_inicio=False):
        if not self.busqueda:
            self.mensaje = "No search query active."
            return

        total = len(self.lineas)

        if desde_inicio:
            fila = 0
            col = 0
        else:
            fila = self.cursor_fila
            col = self.cursor_col + 1

        inicio = (fila, col)

        while True:
            idx = self.lineas[fila].find(self.busqueda, col)

            if idx != -1:
                self.cursor_fila = fila
                self.cursor_col = idx
                self.mensaje = "Found."
                return

            fila += 1
            col = 0

            if fila >= total:
                fila = 0

            if (fila, col) == inicio:
                self.mensaje = "Not found."
                return

    # ------------------------------------------------------------
    # Ventanas simples con borde ASCII
    # ------------------------------------------------------------
    def dibujar_ventana(self, x, y, ancho, alto, titulo_txt=""):
        borde_sup = "╔" + "═" * (ancho - 2) + "╗"
        borde_inf = "╚" + "═" * (ancho - 2) + "╝"
        borde_med = "║" + " " * (ancho - 2) + "║"

        escribir_attr(self.stdscr, x, y, borde_sup, C_VENTANA_BORDE, curses.A_BOLD)

        for fila in range(1, alto - 1):
            escribir(self.stdscr, x, y + fila, borde_med, C_VENTANA)
            escribir_attr(self.stdscr, x, y + fila, "║", C_VENTANA_BORDE, curses.A_BOLD)
            escribir_attr(self.stdscr, x + ancho - 1, y + fila, "║", C_VENTANA_BORDE, curses.A_BOLD)

        escribir_attr(self.stdscr, x, y + alto - 1, borde_inf, C_VENTANA_BORDE, curses.A_BOLD)

        if titulo_txt:
            titulo_visible = " " + titulo_txt[:ancho - 6] + " "
            escribir_attr(self.stdscr, x + 2, y, titulo_visible, C_VENTANA_BORDE, curses.A_BOLD)


    def escribir_en_ventana(self, x, y, ancho, texto, color=C_VENTANA):
        escribir(self.stdscr, x, y, texto[:ancho].ljust(ancho), color)

    # ------------------------------------------------------------
    # Panel para abrir archivos
    # ------------------------------------------------------------
    def listar_panel(self, carpeta):
        entradas = []

        padre = os.path.abspath(os.path.join(carpeta, os.pardir))
        entradas.append({
            "nombre": "..",
            "ruta": padre,
            "tipo": "dir",
        })

        try:
            nombres = os.listdir(carpeta)
        except Exception:
            return entradas

        dirs = []
        archivos = []

        for nombre in nombres:
            ruta = os.path.join(carpeta, nombre)

            if os.path.isdir(ruta) and not nombre.startswith("."):
                dirs.append(nombre)
            elif os.path.isfile(ruta) and nombre.endswith(".py"):
                archivos.append(nombre)

        for nombre in sorted(dirs, key=str.lower):
            entradas.append({
                "nombre": nombre + "/",
                "ruta": os.path.join(carpeta, nombre),
                "tipo": "dir",
            })

        for nombre in sorted(archivos, key=str.lower):
            entradas.append({
                "nombre": nombre,
                "ruta": os.path.join(carpeta, nombre),
                "tipo": "file",
            })

        return entradas

    def abrir_desde_panel(self):
        if self.modificado:
            r = self.confirmar_tres_opciones(
                "Unsaved changes. Save first? Y/N/ESC"
            )

            if r == "esc":
                return

            if r == "y":
                if not self.guardar_archivo():
                    return

        ruta = self.panel_archivos(self.carpeta_actual)

        if ruta is None:
            self.mensaje = "Open canceled."
            return

        self.ruta_archivo = normalizar_ruta(ruta)
        self.carpeta_actual = os.path.dirname(self.ruta_archivo) or self.carpeta_actual
        self.cargar_archivo()

        if not self.lineas:
            self.lineas = [""]

        self.cursor_fila = 0
        self.cursor_col = 0
        self.offset_fila = 0
        self.offset_col = 0
        self.modificado = False
        self.limpiar_undo_redo()
        self.mensaje = "File opened."

    def panel_archivos(self, carpeta_inicial):
        carpeta = normalizar_ruta(carpeta_inicial) or os.getcwd()
        seleccion = 0
        offset = 0

        ventana_an = AN - 6
        ventana_al = AL - 4
        vx = 3
        vy = 2

        while True:
            entradas = self.listar_panel(carpeta)

            if not entradas:
                entradas = [{"nombre": "..", "ruta": os.path.dirname(carpeta), "tipo": "dir"}]

            seleccion = max(0, min(seleccion, len(entradas) - 1))

            alto_lista = ventana_al - 6

            if seleccion < offset:
                offset = seleccion
            elif seleccion >= offset + alto_lista:
                offset = seleccion - alto_lista + 1

            self.dibujar()
            self.dibujar_ventana(vx, vy, ventana_an, ventana_al, "Open Python file")

            ruta_visible = carpeta[-(ventana_an - 4):]
            self.escribir_en_ventana(vx + 2, vy + 1, ventana_an - 4, ruta_visible, C_VENTANA_ESTADO)

            fin_lista = min(len(entradas), offset + alto_lista)

            for i in range(offset, fin_lista):
                y = vy + 3 + (i - offset)
                entrada = entradas[i]
                nombre = entrada["nombre"]

                pref = "[D] " if entrada["tipo"] == "dir" else "    "
                texto = (pref + nombre)[:ventana_an - 4]

                if i == seleccion:
                    self.escribir_en_ventana(vx + 2, y, ventana_an - 4, texto, C_VENTANA_SEL)
                elif entrada["tipo"] == "dir":
                    self.escribir_en_ventana(vx + 2, y, ventana_an - 4, texto, C_VENTANA_DIR)
                else:
                    self.escribir_en_ventana(vx + 2, y, ventana_an - 4, texto, C_VENTANA)

            pie = "ENTER open  ESC cancel"
            self.escribir_en_ventana(vx + 2, vy + ventana_al - 2, ventana_an - 4, pie, C_VENTANA_ESTADO)

            self.stdscr.refresh()
            tecla = self.stdscr.getch()

            if tecla == 27:
                return None

            if tecla == curses.KEY_UP:
                seleccion = max(0, seleccion - 1)
            elif tecla == curses.KEY_DOWN:
                seleccion = min(len(entradas) - 1, seleccion + 1)
            elif tecla == curses.KEY_PPAGE:
                seleccion = max(0, seleccion - alto_lista)
            elif tecla == curses.KEY_NPAGE:
                seleccion = min(len(entradas) - 1, seleccion + alto_lista)
            elif tecla in (10, 13, curses.KEY_ENTER):
                entrada = entradas[seleccion]

                if entrada["tipo"] == "dir":
                    carpeta = normalizar_ruta(entrada["ruta"])
                    seleccion = 0
                    offset = 0
                else:
                    return entrada["ruta"]

    # ------------------------------------------------------------
    # Entrada editable en barra inferior
    # ------------------------------------------------------------
    def input_barra(self, prompt, inicial=""):
        texto = list(inicial)
        pos = len(texto)
        offset = 0

        curses.curs_set(1)

        while True:
            ancho_input = max(1, AN - len(prompt))

            if pos < offset:
                offset = pos
            elif pos > offset + ancho_input:
                offset = pos - ancho_input

            frag = "".join(texto[offset:offset + ancho_input])
            visible = prompt + frag

            escribir(self.stdscr, 0, AL - 1, " " * AN, C_TITULO)

            if offset > 0 and len(prompt) < AN:
                visible = prompt[:-1] + "←" + frag if prompt else "←" + frag

            if offset + ancho_input < len(texto):
                visible = visible[:AN - 1] + "→"

            escribir(self.stdscr, 0, AL - 1, visible[:AN].ljust(AN), C_TITULO)

            cursor_x = len(prompt) + (pos - offset)
            cursor_x = max(0, min(cursor_x, AN - 1))

            try:
                self.stdscr.move(AL - 1, cursor_x)
            except curses.error:
                pass

            self.stdscr.refresh()
            tecla = self.stdscr.getch()

            if tecla in (10, 13, curses.KEY_ENTER):
                return "".join(texto)

            if tecla == 27:
                return None

            if tecla == curses.KEY_LEFT:
                pos = max(0, pos - 1)
                continue

            if tecla == curses.KEY_RIGHT:
                pos = min(len(texto), pos + 1)
                continue

            if tecla == curses.KEY_HOME:
                pos = 0
                continue

            if tecla == curses.KEY_END:
                pos = len(texto)
                continue

            if tecla in (curses.KEY_BACKSPACE, 127, 8):
                if pos > 0:
                    del texto[pos - 1]
                    pos -= 1
                continue

            if tecla == curses.KEY_DC:
                if pos < len(texto):
                    del texto[pos]
                continue

            if 32 <= tecla <= 126:
                texto.insert(pos, chr(tecla))
                pos += 1

    # ------------------------------------------------------------
    # Ayuda y confirmaciones
    # ------------------------------------------------------------
    def mostrar_ayuda(self):
        lineas = [
            "Main",
            "  ALT+M        open menu",
            "  ESC          open menu",
            "",
            "File",
            "  ALT+S        save",
            "  ALT+O        open",
            "",
            "Edit",
            "  ALT+U        undo",
            "  ALT+Y        redo",
            "  ALT+C/X/V    copy / cut / paste line",
            "  ALT+D        duplicate line",
            "",
            "Search / Run",
            "  ALT+F        find",
            "  ALT+N        find next",
            "  ALT+R        run file",
        ]

        ancho = 47
        alto = 21
        x = (AN - ancho) // 2
        y = (AL - alto) // 2

        self.dibujar()
        self.dibujar_ventana(x, y, ancho, alto, "Help")

        for i, linea in enumerate(lineas[:alto - 3]):
            color = C_VENTANA_ESTADO if linea and not linea.startswith(" ") else C_VENTANA
            self.escribir_en_ventana(
                x + 2,
                y + 1 + i,
                ancho - 4,
                linea,
                color
            )

        pie = "ENTER/ESC close"
        self.escribir_en_ventana(x + 2, y + alto - 2, ancho - 4, pie, C_VENTANA_ESTADO)

        self.stdscr.refresh()

        while True:
            tecla = self.stdscr.getch()

            if tecla in (27, 10, 13, curses.KEY_ENTER):
                return None


    def confirmar_simple(self, mensaje):
        escribir(self.stdscr, 0, AL - 1, " " * AN, C_TITULO)
        escribir(self.stdscr, 0, AL - 1, mensaje[:AN], C_TITULO)
        self.stdscr.refresh()

        while True:
            tecla = self.stdscr.getch()

            if tecla in (ord("y"), ord("Y")):
                return True

            if tecla in (ord("n"), ord("N"), 27):
                return False

    def confirmar_tres_opciones(self, mensaje):
        escribir(self.stdscr, 0, AL - 1, " " * AN, C_TITULO)
        escribir(self.stdscr, 0, AL - 1, mensaje[:AN], C_TITULO)
        self.stdscr.refresh()

        while True:
            tecla = self.stdscr.getch()

            if tecla in (ord("y"), ord("Y")):
                return "y"

            if tecla in (ord("n"), ord("N")):
                return "n"

            if tecla == 27:
                return "esc"

    def confirmar_salida(self):
        if not self.modificado:
            return True

        r = self.confirmar_tres_opciones("Save changes before exit? Y/N/ESC")

        if r == "esc":
            return False

        if r == "n":
            return True

        # Al salir, siempre mostramos el nombre en un campo editable.
        # Si era un archivo abierto, aparece su nombre.
        # Si era un archivo nuevo, aparece vacio.
        return self.guardar_como()


def main(stdscr):
    if len(sys.argv) >= 2:
        ruta = sys.argv[1]
    else:
        ruta = None

    ejecutar(stdscr, ruta)


if __name__ == "__main__":
    curses.wrapper(main)
