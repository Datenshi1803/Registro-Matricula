# Sistema Académico - Registro y Análisis de Datos Importaciones 
#V.1.1
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

ventana = tk.Tk()
ventana.title("Sistema Académico - Registro")

# Aumentar tamaño para gráficos grandes
ancho_ventana = 1100
alto_ventana = 750

# Obtener dimensiones de pantalla
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()

# Calcular posición centrada
x = (ancho_pantalla // 2) - (ancho_ventana // 2)
y = (alto_pantalla // 2) - (alto_ventana // 2)

# Aplicar geometría y fondo
ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
ventana.config(bg="#f3f6fa")

# Obtener tamaño de pantalla
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()

# Calcular posición centrada
x = (ancho_pantalla // 2) - (ancho_ventana // 2)
y = (alto_pantalla // 2) - (alto_ventana // 2)
ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

# Crear pestañas
tabs = ttk.Notebook(ventana)
tab_registro = ttk.Frame(tabs)
tab_graficas = ttk.Frame(tabs)
tabs.add(tab_registro, text="📋 Registro")
tabs.add(tab_graficas, text="📊 Gráficas")
tabs.pack(expand=1, fill="both")

# Estilos
style = ttk.Style()
style.theme_use("clam")

style.configure("TLabel", background="#f3f6fa", font=("Segoe UI", 10))
style.configure("TEntry", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#1976D2", foreground="white")
style.map("TButton", background=[("active", "#1565C0")])

# Marco principal
frame = ttk.Frame(tab_registro, padding=20)
frame.pack(expand=True, fill="both")

#Generación de graficas
def generar_grafica(tipo):
    # Leer datos desde SQLite
    conn = sqlite3.connect("registro.db")
    df = pd.read_sql_query("SELECT * FROM registros", conn)
    conn.close()

    if df.empty:
        messagebox.showwarning("Sin datos", "No hay registros disponibles.")
        return

    nivel = nivel_filtro.get().strip()
    asignatura = asignatura_filtro.get().strip()
    anio = anio_filtro.get().strip()

    # Filtrar si hay datos en los campos
    if nivel:
        df = df[df['nivel'].str.contains(nivel, case=False)]
    if asignatura:
        df = df[df['asignatura'].str.contains(asignatura, case=False)]
    if anio:
        df = df[df['anio'].astype(str) == anio]

    if df.empty:
        messagebox.showwarning("Sin resultados", "No se encontraron registros con los filtros seleccionados.")
        return

    # Crear figura
    fig, ax = plt.subplots(figsize=(6, 4.5))

    # ====== NUEVA LÓGICA DE AGRUPACIÓN ======
    if tipo == "Aprobados por nivel y año":
        datos = df.groupby("nivel")["aprobados"].sum()
        titulo = "Aprobados por Nivel y Año"

    elif tipo == "Reprobados por nivel y año":
        datos = df.groupby("nivel")["reprobados"].sum()
        titulo = "Reprobados por Nivel y Año"

    elif tipo == "Aprobados por nivel y asignatura":
        datos = df.groupby("asignatura")["aprobados"].sum()
        titulo = "Aprobados por Asignatura"

    elif tipo == "Reprobados por nivel y asignatura":
        datos = df.groupby("asignatura")["reprobados"].sum()
        titulo = "Reprobados por Asignatura"

    else:
        messagebox.showinfo("Selecciona un tipo", "Por favor selecciona un tipo de gráfica válido.")
        return

    if datos.empty or datos.sum() == 0:
        messagebox.showinfo("Sin datos", "No hay valores para graficar en esta categoría.")
        return

    # ====== FORMATO DE ETIQUETAS ======
    total = datos.sum()

    def formato_etiqueta(porcentaje, valores=datos):
        valor = int(round(porcentaje * total / 100.0))
        # Busca el índice actual y arma el texto
        return f"{valor} ({porcentaje:.1f}%)"

    # ====== GRÁFICO DE PASTEL ======
    wedges, texts, autotexts = ax.pie(
        datos,
        labels=datos.index,
        autopct=lambda p: formato_etiqueta(p),
        startangle=90,
        textprops={'color': 'black', 'fontsize': 9}
    )

    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.axis('equal')  # Mantiene la forma circular

    # ====== LEYENDA ======
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        title="Categorías",
        labels=[f"{cat}: {val}" for cat, val in zip(datos.index, datos)],
        fontsize=9
    )
    
    # Ajuste automático de márgenes para que todo sea visible
    fig.tight_layout(pad=2.0)
    fig.subplots_adjust(right=0.75, top=0.9, bottom=0.1)


    # Limpiar frame anterior
    for widget in frame_preview.winfo_children():
        widget.destroy()

    # Mostrar gráfica en interfaz (ajustada y expandible)
    canvas = FigureCanvasTkAgg(fig, master=frame_preview)
    canvas.draw()

    # Ajuste dinámico para que se vea completa
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(expand=True, fill="both", padx=20, pady=15)

    # Forzar que el gráfico se redibuje al cambiar el tamaño de la ventana
    def on_resize(event):
        fig.tight_layout()
        canvas.draw()

    frame_preview.bind("<Configure>", on_resize)
    # Guardar último dataset y título para exportación
    global ultimo_dato, ultimo_titulo
    ultimo_dato, ultimo_titulo = datos, titulo

    # Mostrar botones de exportación solo después de generar la gráfica
    boton_excel.grid()
    boton_word.grid()



import os
from docx import Document

def exportar_a_excel(datos, tipo):
    nombre_archivo = f"grafica_{tipo.replace(' ', '_')}.xlsx"
    df_export = pd.DataFrame(datos)
    df_export.to_excel(nombre_archivo)
    messagebox.showinfo("Exportado", f"Gráfica exportada como {nombre_archivo}")

def exportar_a_word(datos, tipo):
    nombre_archivo = f"grafica_{tipo.replace(' ', '_')}.docx"
    doc = Document()
    doc.add_heading("Reporte de Gráfica", level=1)
    doc.add_paragraph(f"Tipo: {tipo}")

    tabla = doc.add_table(rows=1, cols=2)
    hdr_cells = tabla.rows[0].cells
    hdr_cells[0].text = "Categoría"
    hdr_cells[1].text = "Valor"

    for index, value in datos.items():
        row_cells = tabla.add_row().cells
        row_cells[0].text = str(index)
        row_cells[1].text = str(value)

    doc.save(nombre_archivo)
    messagebox.showinfo("Exportado", f"Gráfica exportada como {nombre_archivo}")


# Variables para filtros
nivel_filtro = tk.StringVar()
asignatura_filtro = tk.StringVar()
anio_filtro = tk.StringVar()
tipo_filtro = tk.StringVar()

frame_graf = ttk.Frame(tab_graficas, padding=20)
frame_graf.pack(expand=True, fill="both")

# Título
ttk.Label(frame_graf, text="Análisis de Resultados", font=("Segoe UI", 14, "bold"), foreground="#1976D2").grid(row=0, column=0, columnspan=4, pady=10)

# Filtros
ttk.Label(frame_graf, text="Nivel:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
ttk.Entry(frame_graf, textvariable=nivel_filtro, width=25).grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_graf, text="Asignatura:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
ttk.Entry(frame_graf, textvariable=asignatura_filtro, width=25).grid(row=1, column=3, padx=5, pady=5)

ttk.Label(frame_graf, text="Año:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
ttk.Entry(frame_graf, textvariable=anio_filtro, width=25).grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_graf, text="Tipo de gráfica:").grid(row=2, column=2, sticky="e", padx=5, pady=5)
ttk.Combobox(frame_graf, textvariable=tipo_filtro, values=[
    "Aprobados por nivel y año",
    "Reprobados por nivel y año",
    "Aprobados por nivel y asignatura",
    "Reprobados por nivel y asignatura"
], state="readonly", width=23).grid(row=2, column=3, padx=5, pady=5)

# --- Botón de generar y botones de exportación ---
boton_generar = ttk.Button(
    frame_graf,
    text="📈 Generar gráfica",
    command=lambda: generar_grafica(tipo_filtro.get())
)
boton_generar.grid(row=3, column=0, pady=15, padx=5, sticky="w")

# Botones de exportación (inicialmente ocultos)
boton_excel = ttk.Button(frame_graf, text="📤 Exportar a Excel", command=lambda: exportar_a_excel(ultimo_dato, ultimo_titulo))
boton_word = ttk.Button(frame_graf, text="📝 Exportar a Word", command=lambda: exportar_a_word(ultimo_dato, ultimo_titulo))

# No se muestran aún
boton_excel.grid(row=3, column=2, pady=15, padx=5, sticky="e")
boton_word.grid(row=3, column=3, pady=15, padx=5, sticky="e")

boton_excel.grid_remove()
boton_word.grid_remove()

# Área de vista previa
frame_preview = ttk.Frame(frame_graf)
frame_preview.grid(row=4, column=0, columnspan=4, pady=10)

# Título
ttk.Label(frame, text="Registro Académico", font=("Segoe UI", 16, "bold"), background="#f3f6fa", foreground="#1976D2").grid(
    row=0, column=0, columnspan=4, pady=10
)

# Variables
campos = [
    ("Nivel", tk.StringVar()), ("Profesor", tk.StringVar()),
    ("Asignatura", tk.StringVar()), ("Año", tk.StringVar()),
    ("Trimestre", tk.StringVar()), ("Turno", tk.StringVar()),
    ("Hombres", tk.StringVar()), ("Mujeres", tk.StringVar()),
    ("Aprobados", tk.StringVar()), ("Reprobados", tk.StringVar()),
    ("Reprobados a la fecha", tk.StringVar()), ("Sin asistencia", tk.StringVar()),
    ("Sin calificación", tk.StringVar()), ("Sin profesor", tk.StringVar()),
    ("Retirados", tk.StringVar())
]

# Dividir en 2 columnas visuales
col_izq = campos[:8]
col_der = campos[8:]

# Subtítulos
ttk.Label(frame, text="Datos Generales", font=("Segoe UI", 11, "bold"), foreground="#0D47A1").grid(row=1, column=0, sticky="w", pady=5)
ttk.Label(frame, text="Estadísticas", font=("Segoe UI", 11, "bold"), foreground="#0D47A1").grid(row=1, column=2, sticky="w", pady=5)

# ==========================
# VALIDACIÓN DE ENTRADAS
# ==========================
def solo_numeros(valor):
    """Permite solo números o vacío (para borrar)."""
    if valor == "" or valor.isdigit():
        return True
    else:
        ventana.bell()  # sonido de error opcional
        return False

vcmd = ventana.register(solo_numeros)

# ==========================
# CAMPOS DE FORMULARIO
# ==========================

# Variables
campos = [
    ("Nivel", tk.StringVar()), ("Profesor", tk.StringVar()),
    ("Asignatura", tk.StringVar()), ("Año", tk.StringVar()),
    ("Trimestre", tk.StringVar()), ("Turno", tk.StringVar()),
    ("Hombres", tk.StringVar()), ("Mujeres", tk.StringVar()),
    ("Aprobados", tk.StringVar()), ("Reprobados", tk.StringVar()),
    ("Reprobados a la fecha", tk.StringVar()), ("Sin asistencia", tk.StringVar()),
    ("Sin calificación", tk.StringVar()), ("Sin profesor", tk.StringVar()),
    ("Retirados", tk.StringVar())
]

# Dividir en columnas
col_izq = campos[:8]
col_der = campos[8:]

# Subtítulos
ttk.Label(frame, text="Datos Generales", font=("Segoe UI", 11, "bold"), foreground="#0D47A1").grid(row=1, column=0, sticky="w", pady=5)
ttk.Label(frame, text="Estadísticas", font=("Segoe UI", 11, "bold"), foreground="#0D47A1").grid(row=1, column=2, sticky="w", pady=5)

# Columna izquierda
for i, (label, var) in enumerate(col_izq, start=2):
    ttk.Label(frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)

    # Campos de texto y combos
    if label == "Turno":
        ttk.Combobox(frame, textvariable=var, values=["Mañana", "Tarde"], state="readonly", width=23).grid(row=i, column=1, sticky="w", padx=5, pady=5)
    elif label == "Trimestre":
        ttk.Combobox(frame, textvariable=var, values=["1", "2", "3"], state="readonly", width=23).grid(row=i, column=1, sticky="w", padx=5, pady=5)
    elif label == "Año":
        import datetime
        anios = [str(a) for a in range(2020, datetime.date.today().year + 2)]
        cb = ttk.Combobox(frame, textvariable=var, values=anios, state="readonly", width=23)
        cb.grid(row=i, column=1, sticky="w", padx=5, pady=5)
        cb.set(str(datetime.date.today().year))
    else:
        # Si el campo es numérico (a partir de "Hombres")
        if label in ["Hombres", "Mujeres", "Aprobados", "Reprobados", "Reprobados a la fecha",
                     "Sin asistencia", "Sin calificación", "Sin profesor", "Retirados"]:
            ttk.Entry(frame, textvariable=var, width=25, validate="key", validatecommand=(vcmd, "%P")).grid(row=i, column=1, sticky="w", padx=5, pady=5)
        else:
            ttk.Entry(frame, textvariable=var, width=25).grid(row=i, column=1, sticky="w", padx=5, pady=5)

# Columna derecha
for i, (label, var) in enumerate(col_der, start=2):
    ttk.Label(frame, text=label).grid(row=i, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame, textvariable=var, width=25, validate="key", validatecommand=(vcmd, "%P")).grid(row=i, column=3, sticky="w", padx=5, pady=5)


# Separador
ttk.Separator(frame, orient="horizontal").grid(row=18, column=0, columnspan=4, sticky="ew", pady=10)

# ==========================
# FUNCIONES
# ==========================

def guardar_datos():
    try:
        conn = sqlite3.connect("registro.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nivel TEXT, profesor TEXT, asignatura TEXT, anio INTEGER,
            trimestre INTEGER, turno TEXT, hombres INTEGER, mujeres INTEGER,
            aprobados INTEGER, reprobados INTEGER, reprobados_fecha INTEGER,
            sin_asistencia INTEGER, sin_calificacion INTEGER, sin_profesor INTEGER,
            retirados INTEGER
        )
        """)

        valores = [v.get() for _, v in campos]
        cursor.execute("""
        INSERT INTO registros (nivel, profesor, asignatura, anio, trimestre, turno,
                               hombres, mujeres, aprobados, reprobados, reprobados_fecha,
                               sin_asistencia, sin_calificacion, sin_profesor, retirados)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, valores)

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Datos guardados correctamente en la base de datos.")
        limpiar_campos()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el registro:\n{e}")

def limpiar_campos():
    for _, var in campos:
        var.set("")  # borra el contenido de cada campo

# Botones
ttk.Button(frame, text="Guardar", width=18, command=guardar_datos).grid(row=19, column=0, columnspan=2, pady=10)
ttk.Button(frame, text="Limpiar", width=18, command=limpiar_campos).grid(row=19, column=2, columnspan=2, pady=10)


ventana.mainloop()
