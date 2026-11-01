
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

# Motor original de análisis de Tutor DS
from tutor_ds.report import analyze_source, render_text
# 1. CONFIGURACIÓN VISUAL
COLOR_FONDO = "#F1F5F9"
COLOR_MENU = "#0F172A"
COLOR_PRINCIPAL = "#2563EB"
COLOR_PRINCIPAL_OSCURO = "#1D4ED8"
COLOR_TEXTO = "#1E293B"
COLOR_BLANCO = "#FFFFFF"
COLOR_SECUNDARIO = "#64748B"
COLOR_BORDE = "#E2E8F0"


# 2. VENTANA PRINCIPAL
ventana = tk.Tk()

ventana.title("Tutor DS | Analizador de código Python")
ventana.geometry("1100x700")
ventana.minsize(900, 600)
ventana.configure(bg=COLOR_FONDO)


# 3. ESTRUCTURA PRINCIPAL
contenedor = tk.Frame(
    ventana,
    bg=COLOR_FONDO
)

contenedor.pack(
    fill="both",
    expand=True
)


# Menú lateral
menu_lateral = tk.Frame(
    contenedor,
    bg=COLOR_MENU,
    width=230
)

menu_lateral.pack(
    side="left",
    fill="y"
)

menu_lateral.pack_propagate(False)


# Área de contenido
contenido = tk.Frame(
    contenedor,
    bg=COLOR_FONDO
)

contenido.pack(
    side="left",
    fill="both",
    expand=True
)
# 4. MENÚ LATERAL
titulo_logo = tk.Label(
    menu_lateral,
    text="TUTOR DS",
    font=("Segoe UI", 20, "bold"),
    bg=COLOR_MENU,
    fg=COLOR_BLANCO
)

titulo_logo.pack(
    anchor="w",
    padx=20,
    pady=(30, 5)
)


subtitulo_logo = tk.Label(
    menu_lateral,
    text="Analizador de código",
    font=("Segoe UI", 10),
    bg=COLOR_MENU,
    fg="#94A3B8"
)

subtitulo_logo.pack(
    anchor="w",
    padx=20,
    pady=(0, 30)
)


def crear_boton_menu(texto, funcion):
    """Crea un botón para navegar entre pantallas."""

    boton = tk.Button(
        menu_lateral,
        text=texto,
        font=("Segoe UI", 11),
        bg=COLOR_MENU,
        fg=COLOR_BLANCO,
        activebackground=COLOR_PRINCIPAL,
        activeforeground=COLOR_BLANCO,
        relief="flat",
        anchor="w",
        padx=20,
        pady=12,
        cursor="hand2",
        command=funcion
    )

    boton.pack(
        fill="x",
        padx=10,
        pady=3
    )

    return boton


# 5. ENCABEZADO
encabezado = tk.Frame(
    contenido,
    bg=COLOR_BLANCO,
    height=80
)

encabezado.pack(fill="x")
encabezado.pack_propagate(False)


titulo_pagina = tk.Label(
    encabezado,
    text="Panel principal",
    font=("Segoe UI", 20, "bold"),
    bg=COLOR_BLANCO,
    fg=COLOR_TEXTO
)

titulo_pagina.pack(
    side="left",
    padx=30,
    pady=20
)


# Zona donde se cambiará el contenido
area_principal = tk.Frame(
    contenido,
    bg=COLOR_FONDO
)

area_principal.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=25
)


# 6. FUNCIONES GENERALES
def limpiar_pantalla():
    """Elimina los elementos de la pantalla actual."""

    for elemento in area_principal.winfo_children():
        elemento.destroy()


# 7. PANTALLA PRINCIPAL
def mostrar_inicio():
    """Muestra la pantalla de bienvenida."""

    limpiar_pantalla()

    titulo_pagina.config(
        text="Panel principal"
    )

    tk.Label(
        area_principal,
        text="Bienvenido a Tutor DS",
        font=("Segoe UI", 24, "bold"),
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO
    ).pack(
        anchor="w",
        pady=(10, 5)
    )

    tk.Label(
        area_principal,
        text=(
            "Analiza tu código Python, identifica posibles "
            "defectos de diseño y consulta recomendaciones "
            "de mejora."
        ),
        font=("Segoe UI", 11),
        bg=COLOR_FONDO,
        fg=COLOR_SECUNDARIO,
        wraplength=700,
        justify="left"
    ).pack(
        anchor="w",
        pady=(0, 25)
    )

    # Tarjeta principal
    tarjeta = tk.Frame(
        area_principal,
        bg=COLOR_BLANCO,
        padx=25,
        pady=25,
        highlightbackground=COLOR_BORDE,
        highlightthickness=1
    )

    tarjeta.pack(
        fill="x"
    )

    tk.Label(
        tarjeta,
        text="Análisis estático de código",
        font=("Segoe UI", 15, "bold"),
        bg=COLOR_BLANCO,
        fg=COLOR_TEXTO
    ).pack(
        anchor="w",
        pady=(0, 10)
    )

    tk.Label(
        tarjeta,
        text=(
            "Carga un archivo Python o escribe código en el "
            "editor. Tutor DS analizará el código utilizando "
            "el motor del proyecto y generará un informe."
        ),
        font=("Segoe UI", 11),
        bg=COLOR_BLANCO,
        fg=COLOR_SECUNDARIO,
        wraplength=700,
        justify="left"
    ).pack(
        anchor="w"
    )

    tk.Button(
        tarjeta,
        text="Analizar código",
        command=mostrar_analizador,
        bg=COLOR_PRINCIPAL,
        fg=COLOR_BLANCO,
        activebackground=COLOR_PRINCIPAL_OSCURO,
        activeforeground=COLOR_BLANCO,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=18,
        pady=10,
        cursor="hand2"
    ).pack(
        anchor="w",
        pady=(20, 0)
    )


# 8. PANTALLA DEL ANALIZADOR
def mostrar_analizador():
    """Permite escribir, cargar y analizar código Python."""

    limpiar_pantalla()

    titulo_pagina.config(
        text="Analizar código"
    )

    tk.Label(
        area_principal,
        text="Código fuente Python",
        font=("Segoe UI", 18, "bold"),
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO
    ).pack(
        anchor="w",
        pady=(0, 5)
    )

    tk.Label(
        area_principal,
        text=(
            "Escribe código Python o selecciona un archivo "
            "con extensión .py."
        ),
        font=("Segoe UI", 10),
        bg=COLOR_FONDO,
        fg=COLOR_SECUNDARIO
    ).pack(
        anchor="w",
        pady=(0, 15)
    )

    # Barra de herramientas
    barra_botones = tk.Frame(
        area_principal,
        bg=COLOR_FONDO
    )

    barra_botones.pack(
        fill="x",
        pady=(0, 10)
    )

    # Nombre del archivo seleccionado
    nombre_archivo = tk.Label(
        barra_botones,
        text="Sin archivo seleccionado",
        font=("Segoe UI", 9),
        bg=COLOR_FONDO,
        fg=COLOR_SECUNDARIO
    )

    # Contenedor del editor
    marco_editor = tk.Frame(
        area_principal,
        bg=COLOR_BLANCO,
        highlightbackground=COLOR_BORDE,
        highlightthickness=1
    )

    marco_editor.pack(
        fill="both",
        expand=True
    )

    # Editor de código
    editor = tk.Text(
        marco_editor,
        font=("Consolas", 11),
        bg=COLOR_BLANCO,
        fg=COLOR_TEXTO,
        insertbackground=COLOR_TEXTO,
        relief="flat",
        wrap="none",
        undo=True,
        padx=12,
        pady=12
    )

    editor.pack(
        side="left",
        fill="both",
        expand=True
    )

    # Barra de desplazamiento vertical
    scroll_vertical = tk.Scrollbar(
        marco_editor,
        orient="vertical",
        command=editor.yview
    )

    scroll_vertical.pack(
        side="right",
        fill="y"
    )

    editor.configure(
        yscrollcommand=scroll_vertical.set
    )

    # Barra de desplazamiento horizontal
    scroll_horizontal = tk.Scrollbar(
        area_principal,
        orient="horizontal",
        command=editor.xview
    )

    editor.configure(
        xscrollcommand=scroll_horizontal.set
    )

    scroll_horizontal.pack(
        fill="x"
    )

    # Código inicial de ejemplo
    editor.insert(
        "1.0",
        "# Escribe aquí tu código Python\n\n"
        "def saludar(nombre):\n"
        "    return 'Hola ' + nombre\n\n"
        "print(saludar('Mundo'))\n"
    )

 
    # CARGAR ARCHIVO
    def cargar_archivo():
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Python",
            filetypes=[
                ("Archivos Python", "*.py"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not ruta:
            return

        try:
            codigo_archivo = Path(ruta).read_text(
                encoding="utf-8"
            )

            editor.delete(
                "1.0",
                tk.END
            )

            editor.insert(
                "1.0",
                codigo_archivo
            )

            nombre_archivo.config(
                text=f"Archivo: {Path(ruta).name}"
            )

        except (OSError, UnicodeError) as error:
            messagebox.showerror(
                "Error al abrir el archivo",
                f"No se pudo leer el archivo:\n\n{error}"
            )

    tk.Button(
        barra_botones,
        text="Cargar archivo .py",
        command=cargar_archivo,
        bg=COLOR_BLANCO,
        fg=COLOR_TEXTO,
        activebackground=COLOR_BORDE,
        relief="solid",
        bd=1,
        padx=12,
        pady=7,
        cursor="hand2"
    ).pack(
        side="left"
    )

    nombre_archivo.pack(
        side="left",
        padx=12
    )

    # ANALIZAR CÓDIGO
    def analizar_codigo():
        codigo = editor.get(
            "1.0",
            "end-1c"
        ).strip()

        if not codigo:
            messagebox.showwarning(
                "Código vacío",
                "Escribe o carga código antes de analizar."
            )
            return

        try:
            # Ejecutar el motor original del proyecto.
            resultado = analyze_source(codigo)

            # Transformar el resultado en un informe legible.
            informe = render_text(resultado)

            # Mostrar el informe en una nueva ventana.
            mostrar_resultados(informe)

        except Exception as error:
            messagebox.showerror(
                "Error durante el análisis",
                (
                    "No fue posible completar el análisis.\n\n"
                    f"Detalle: {error}"
                )
            )

    tk.Button(
        area_principal,
        text="Analizar código",
        command=analizar_codigo,
        bg=COLOR_PRINCIPAL,
        fg=COLOR_BLANCO,
        activebackground=COLOR_PRINCIPAL_OSCURO,
        activeforeground=COLOR_BLANCO,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padx=20,
        pady=10,
        cursor="hand2"
    ).pack(
        anchor="e",
        pady=(12, 0)
    )
# 9. VENTANA DE RESULTADOS
def mostrar_resultados(informe):
    """Presenta el informe del analizador en otra ventana."""

    ventana_resultados = tk.Toplevel(ventana)

    ventana_resultados.title(
        "Tutor DS | Resultados del análisis"
    )

    ventana_resultados.geometry("850x600")
    ventana_resultados.minsize(600, 400)
    ventana_resultados.configure(
        bg=COLOR_FONDO
    )

    tk.Label(
        ventana_resultados,
        text="Resultados del análisis",
        font=("Segoe UI", 20, "bold"),
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO
    ).pack(
        anchor="w",
        padx=20,
        pady=(20, 5)
    )

    tk.Label(
        ventana_resultados,
        text=(
            "Informe generado por el motor de análisis de Tutor DS."
        ),
        font=("Segoe UI", 10),
        bg=COLOR_FONDO,
        fg=COLOR_SECUNDARIO
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 15)
    )

    # Panel del informe
    marco_resultados = tk.Frame(
        ventana_resultados,
        bg=COLOR_BLANCO,
        highlightbackground=COLOR_BORDE,
        highlightthickness=1
    )

    marco_resultados.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
    )

    texto_resultados = tk.Text(
        marco_resultados,
        font=("Consolas", 10),
        bg=COLOR_BLANCO,
        fg=COLOR_TEXTO,
        wrap="word",
        padx=15,
        pady=15,
        relief="flat"
    )

    texto_resultados.pack(
        side="left",
        fill="both",
        expand=True
    )

    scroll_resultados = tk.Scrollbar(
        marco_resultados,
        orient="vertical",
        command=texto_resultados.yview
    )

    scroll_resultados.pack(
        side="right",
        fill="y"
    )

    texto_resultados.configure(
        yscrollcommand=scroll_resultados.set
    )

    texto_resultados.insert(
        "1.0",
        str(informe)
    )

    # El informe queda en modo de solo lectura.
    texto_resultados.configure(
        state="disabled"
    )

# 10. BOTONES DE NAVEGACIÓN
crear_boton_menu(
    "⌂   Panel principal",
    mostrar_inicio
)

crear_boton_menu(
    "</>  Analizar código",
    mostrar_analizador
)

# 11. INICIAR APLICACIÓN
mostrar_inicio()

ventana.mainloop()
