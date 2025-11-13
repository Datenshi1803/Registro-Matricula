# Sistema Académico - Registro y Análisis de Datos Importaciones 
#V.1.1
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk 
import sqlite3
import pandas as pd 
import os
import datetime
from docx import Document
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Separar las importaciones y añadir ImageDraw para transparencia
from ttkbootstrap.constants import *
from PIL import Image, ImageTk, ImageDraw # ¡Añadido ImageDraw para transparencia!

# =========================================================
# CONFIGURACIÓN GLOBAL 

# =========================================================
# Usamos ttk.Window para aplicar un tema completo (flatly es moderno y claro)
ventana = ttk.Window(title="Sistema Académico - Registro", themename="flatly") 

# Aumentar tamaño para gráficos grandes
ancho_ventana = 1100
alto_ventana = 750

# Ruta de la imagen de fondo (Usando la ruta corregida)
IMAGEN_PATH = "fondo_cefine.png"

# Opcional: Define el nivel de opacidad (0 = invisible, 255 = totalmente opaco)
OPACIDAD_NIVEL = 90  # Un valor bajo (90) para que sea transparente.

# Obtener dimensiones de pantalla y centrar la ventana
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()
x = (ancho_pantalla // 2) - (ancho_ventana // 2)
y = (alto_pantalla // 2) - (alto_ventana // 2)
ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")


# Función para cargar y establecer la imagen de fondo CON OPACIDAD
def establecer_fondo(contenedor, imagen_path):
    try:
        # 1. Cargar imagen con Pillow y convertir a RGBA para manejar transparencia
        img = Image.open(imagen_path).convert("RGBA")
        
        # Obtenemos las dimensiones actuales (o iniciales) del contenedor
        # Usamos winfo_reqwidth/height si winfo_width/height es 1 (al inicio)
        contenedor.update_idletasks()
        current_width = contenedor.winfo_width()
        current_height = contenedor.winfo_height()
        
        # 2. Redimensionar al tamaño del contenedor
        img_redim = img.resize((current_width, current_height)) 
        
        # 3. Crear una capa de opacidad (alpha channel) y aplicar el nivel
        alpha = img_redim.split()[3]
        alpha = Image.eval(alpha, lambda x: x * (OPACIDAD_NIVEL / 255))
        img_redim.putalpha(alpha)
        
        # 4. Convertir para Tkinter
        fondo_img = ImageTk.PhotoImage(img_redim)
        
        # 5. Crear un Label que contendrá la imagen
        # Usamos tk.Label, que tiene un fondo por defecto más fácil de ignorar que ttk.Label.
        fondo_label = tk.Label(contenedor, image=fondo_img, borderwidth=0)
        fondo_label.image = fondo_img # Mantener referencia
        
        # 6. Usar .place para que ocupe todo el fondo
        fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 7. ESTO ES CLAVE: Mover el Label de la imagen a la capa inferior.
        fondo_label.lower() 
        
        # Opcional: Función de redimensionado dinámico (actualizada para la opacidad)
        def resize_image(event):
            try:
                new_width = event.width
                new_height = event.height
                
                # Recargar y redimensionar la imagen original
                img_resized = Image.open(imagen_path).convert("RGBA").resize((new_width, new_height))
                
                # Reaplicar opacidad en el redimensionamiento
                alpha_resized = img_resized.split()[3]
                alpha_resized = Image.eval(alpha_resized, lambda x: x * (OPACIDAD_NIVEL / 255))
                img_resized.putalpha(alpha_resized)

                new_image = ImageTk.PhotoImage(img_resized)
                
                fondo_label.config(image=new_image)
                fondo_label.image = new_image
                fondo_label.lower() 
            except Exception:
                pass 
            
        contenedor.bind('<Configure>', resize_image)
        
    except FileNotFoundError:
        print(f"Advertencia: Archivo de fondo no encontrado en {imagen_path}. No se aplicará fondo.")
    except Exception as e:
        print(f"Error al cargar la imagen de fondo con opacidad: {e}")

# Crear pestañas
tabs = ttk.Notebook(ventana)
tab_registro = ttk.Frame(tabs, padding=15) 
tab_graficas = ttk.Frame(tabs, padding=15) 
tabs.add(tab_registro, text="📋 Registro")
tabs.add(tab_graficas, text="📊 Gráficas")
tabs.pack(expand=1, fill="both", padx=10, pady=10) 


# Marco principal de REGISTRO (dentro del tab_registro)
# bootstyle='light' ayuda a que el fondo del frame sea claro y la imagen se vea.
frame = ttk.Frame(tab_registro, padding=20, borderwidth=1, relief="flat", bootstyle='light') 
frame.pack(expand=True, fill="both")

# APLICAR FONDO EN EL FRAME DE REGISTRO
#establecer_fondo(frame, IMAGEN_PATH)


# >>> INICIO DE RESPONSIVIDAD: REGISTRO (frame) <<<
frame.columnconfigure(1, weight=1)
frame.columnconfigure(3, weight=1)
frame.rowconfigure(18, weight=1) 
# >>> FIN DE RESPONSIVIDAD: REGISTRO (frame) <<<


# Marco de Gráficas (dentro del tab_graficas)
frame_graf = ttk.Frame(tab_graficas, padding=20, bootstyle='light') 
frame_graf.pack(expand=True, fill="both")

# APLICAR FONDO EN EL FRAME DE GRÁFICAS
establecer_fondo(frame_graf, IMAGEN_PATH)

# >>> INICIO DE RESPONSIVIDAD: GRÁFICAS (frame_graf) <<<
frame_graf.columnconfigure(1, weight=1)
frame_graf.columnconfigure(3, weight=1)
frame_graf.rowconfigure(4, weight=5) 
# >>> FIN DE RESPONSIVIDAD: GRÁFICAS (frame_graf) <<<


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

    # ====== LÓGICA DE AGRUPACIÓN ======
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

# Título (usando el estilo primario de bootstrap para darle color)
ttk.Label(frame_graf, text="Análisis de Resultados", font=("Segoe UI", 14, "bold"), style='primary.TLabel').grid(row=0, column=0, columnspan=4, pady=10)

# Filtros (Los Entry y Combobox ya tienen bordes redondeados por el tema)
ttk.Label(frame_graf, text="Nivel:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
ttk.Entry(frame_graf, textvariable=nivel_filtro, width=25).grid(row=1, column=1, padx=5, pady=5, sticky="ew") # sticky="ew" para expansión

ttk.Label(frame_graf, text="Asignatura:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
ttk.Entry(frame_graf, textvariable=asignatura_filtro, width=25).grid(row=1, column=3, padx=5, pady=5, sticky="ew") # sticky="ew" para expansión

ttk.Label(frame_graf, text="Año:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
ttk.Entry(frame_graf, textvariable=anio_filtro, width=25).grid(row=2, column=1, padx=5, pady=5, sticky="ew") # sticky="ew" para expansión

ttk.Label(frame_graf, text="Tipo de gráfica:").grid(row=2, column=2, sticky="e", padx=5, pady=5)
ttk.Combobox(frame_graf, textvariable=tipo_filtro, values=[
    "Aprobados por nivel y año",
    "Reprobados por nivel y año",
    "Aprobados por nivel y asignatura",
    "Reprobados por nivel y asignatura"
], state="readonly", width=23).grid(row=2, column=3, padx=5, pady=5, sticky="ew") # sticky="ew" para expansión

# --- Botón de generar y botones de exportación ---
boton_generar = ttk.Button(
    frame_graf,
    text="📈 Generar gráfica",
    bootstyle=PRIMARY,
    command=lambda: generar_grafica(tipo_filtro.get())
)
boton_generar.grid(row=3, column=0, pady=15, padx=5, sticky="w")

# Botones de exportación (usamos INFO para un color secundario)
# Se definen 'ultimo_dato' y 'ultimo_titulo' como globales al inicio de la función generar_grafica.
try:
    ultimo_dato = pd.Series()
    ultimo_titulo = ""
except NameError:
    ultimo_dato = pd.Series()
    ultimo_titulo = ""

boton_excel = ttk.Button(frame_graf, text="📤 Exportar a Excel", bootstyle=INFO, command=lambda: exportar_a_excel(ultimo_dato, ultimo_titulo))
boton_word = ttk.Button(frame_graf, text="📝 Exportar a Word", bootstyle=INFO, command=lambda: exportar_a_word(ultimo_dato, ultimo_titulo))

# No se muestran aún
boton_excel.grid(row=3, column=2, pady=15, padx=5, sticky="e")
boton_word.grid(row=3, column=3, pady=15, padx=5, sticky="e")

boton_excel.grid_remove()
boton_word.grid_remove()

# Área de vista previa (se expande gracias a rowconfigure(4, weight=5))
frame_preview = ttk.Frame(frame_graf)
frame_preview.grid(row=4, column=0, columnspan=4, pady=10, sticky="nsew") # sticky="nsew" para expansión


# Marco superior con logo y título
frame_header = ttk.Frame(frame)
frame_header.grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")

# Logo en la parte izquierda
try:
    logo_path = "logo.png"  # Cambia esto a la ruta de tu logo
    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path).convert("RGBA")
        logo_img.thumbnail((80, 80), Image.Resampling.LANCZOS)  # Ajustar tamaño
        logo_tk = ImageTk.PhotoImage(logo_img)
        
        logo_label = tk.Label(frame_header, image=logo_tk, borderwidth=0, bg='white')
        logo_label.image = logo_tk
        logo_label.pack(side="left", padx=10)
except Exception as e:
    print(f"No se pudo cargar el logo: {e}")

# Título
ttk.Label(frame_header, text="Registro Académico", font=("Segoe UI", 16, "bold"), style='primary.TLabel').pack(side="left", padx=10, expand=True)

# Variables (Mantenemos la definición única para evitar duplicados)
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

# Subtítulos (usando el estilo secundario de bootstrap para darle color)
ttk.Label(frame, text="Datos Generales", font=("Segoe UI", 11, "bold"), style='info.TLabel').grid(row=1, column=0, sticky="w", pady=5)
ttk.Label(frame, text="Estadísticas", font=("Segoe UI", 11, "bold"), style='info.TLabel').grid(row=1, column=2, sticky="w", pady=5)
def solo_numeros(valor):
    """Permite solo números o vacío (para borrar)."""
    if valor == "" or valor.isdigit():
        return True
    else:
        ventana.bell() 
        return False

vcmd = ventana.register(solo_numeros)

# ==========================
# CAMPOS DE FORMULARIO
# ==========================
# # Columna izquierda
for i, (label, var) in enumerate(col_izq, start=2):
    ttk.Label(frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)

    # Campos de texto y combos
    if label == "Turno":
        # sticky="ew" permite que el widget se expanda
        ttk.Combobox(frame, textvariable=var, values=["Mañana", "Tarde"], state="readonly", width=23, bootstyle=PRIMARY).grid(row=i, column=1, sticky="ew", padx=5, pady=5)
    elif label == "Trimestre":
        ttk.Combobox(frame, textvariable=var, values=["1", "2", "3"], state="readonly", width=23, bootstyle=PRIMARY).grid(row=i, column=1, sticky="ew", padx=5, pady=5)
    elif label == "Año":
        anios = [str(a) for a in range(2020, datetime.date.today().year + 2)]
        cb = ttk.Combobox(frame, textvariable=var, values=anios, state="readonly", width=23, bootstyle=PRIMARY)
        cb.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
        cb.set(str(datetime.date.today().year))
    else:
        if label in ["Hombres", "Mujeres", "Aprobados", "Reprobados", "Reprobados a la fecha",
                      "Sin asistencia", "Sin calificación", "Sin profesor", "Retirados"]:
            ttk.Entry(frame, textvariable=var, width=25, validate="key", validatecommand=(vcmd, "%P")).grid(row=i, column=1, sticky="ew", padx=5, pady=5)
        else:
            ttk.Entry(frame, textvariable=var, width=25).grid(row=i, column=1, sticky="ew", padx=5, pady=5)

# Columna derecha
for i, (label, var) in enumerate(col_der, start=2):
    ttk.Label(frame, text=label).grid(row=i, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame, textvariable=var, width=25, validate="key", validatecommand=(vcmd, "%P")).grid(row=i, column=3, sticky="ew", padx=5, pady=5) # sticky="ew" para expansión


# Separador (usando el color secundario)
ttk.Separator(frame, orient="horizontal", bootstyle=SECONDARY).grid(row=19, column=0, columnspan=4, sticky="ew", pady=10)

# ==========================
# FUNCIONES
# ==========================

def guardar_datos():
    try:
        # Validación: al menos los campos principales deben tener contenido.
        if not all(v.get() for _, v in campos[:3]): 
             messagebox.showwarning("Advertencia", "Los campos Nivel, Profesor y Asignatura no pueden estar vacíos.")
             return

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

        # Aseguramos que los valores vacíos sean NULL o 0 en la DB
        valores = [v.get() if v.get() else None for _, v in campos] 
        
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

# Botones (usando bootstyle='primary' y 'danger' para mejor estética)
ttk.Button(frame, text="Guardar", width=18, bootstyle=PRIMARY, command=guardar_datos).grid(row=20, column=0, columnspan=2, pady=10)
ttk.Button(frame, text="Limpiar", width=18, bootstyle=DANGER, command=limpiar_campos).grid(row=20, column=2, columnspan=2, pady=10)


ventana.mainloop()