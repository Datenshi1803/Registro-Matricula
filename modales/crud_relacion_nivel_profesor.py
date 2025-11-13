# crud_relacion_nivel_profesor.py
import tkinter as tk
import sqlite3
import ttkbootstrap as ttk
from tkinter import messagebox
from modals import Modal


# ==============================================================
# 🔵 MODAL PRINCIPAL — ASIGNAR NIVELES A PROFESORES
# ==============================================================

def abrir_asignacion_niveles_profesor(ventana):
    modal = Modal(
        parent=ventana,
        title="Asignar Niveles a Profesores",
        width=650,
        height=520
    )

    frame = modal.body

    # -------------------------------
    # SELECCIONAR PROFESOR
    # -------------------------------
    ttk.Label(frame, text="Seleccione Profesor:", font=("Segoe UI", 11, "bold")).pack(anchor="w")
    profesor_var = tk.StringVar()
    cb_prof = ttk.Combobox(frame, textvariable=profesor_var, state="readonly", width=40)
    cb_prof.pack(fill="x", pady=5)

    # Cargar profesores
    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM profesores ORDER BY nombre")
    cb_prof["values"] = [p[0] for p in cursor.fetchall()]
    conn.close()

    # -------------------------------
    # TABLA DE NIVELES ASIGNADOS
    # -------------------------------
    ttk.Label(frame, text="Niveles Asignados:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=10)

    tabla = ttk.Treeview(
        frame,
        columns=("Nivel",),
        show="headings",
        height=10
    )
    tabla.heading("Nivel", text="Nivel")
    tabla.column("Nivel", width=300)
    tabla.pack(fill="both", expand=True)

    # -------------------------------
    # COMBOBOX PARA NUEVA ASIGNACIÓN
    # -------------------------------
    ttk.Label(frame, text="Asignar nuevo nivel:", font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 0))
    nivel_var = tk.StringVar()
    cb_nivel = ttk.Combobox(frame, textvariable=nivel_var, state="readonly", width=40)
    cb_nivel.pack(fill="x", pady=5)

    # Cargar niveles
    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM niveles ORDER BY nombre")
    cb_nivel["values"] = [n[0] for n in cursor.fetchall()]
    conn.close()

    # -------------------------------
    # BOTÓN DE ASIGNAR
    # -------------------------------
    ttk.Button(
        frame,
        text="➕ Asignar Nivel",
        bootstyle="success",
        command=lambda: asignar_nivel(profesor_var, nivel_var, tabla)
    ).pack(pady=10)

    # -------------------------------
    # BOTÓN DE ELIMINAR
    # -------------------------------
    ttk.Button(
        frame,
        text="🗑️ Eliminar Selección",
        bootstyle="danger",
        command=lambda: eliminar_nivel_asignado(profesor_var, tabla)
    ).pack(pady=5)

    # Recargar niveles del profesor al seleccionarlo
    cb_prof.bind(
        "<<ComboboxSelected>>",
        lambda e: cargar_niveles_de_profesor(profesor_var, tabla)
    )



# ==============================================================
# 🟣 FUNCIONES CRUD
# ==============================================================

def cargar_niveles_de_profesor(profesor_var, tabla):
    """Carga los niveles asociados a un profesor."""
    tabla.delete(*tabla.get_children())
    profesor = profesor_var.get()

    if not profesor:
        return

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT niveles.nombre
        FROM niveles
        JOIN nivel_profesor ON niveles.id = nivel_profesor.id_nivel
        JOIN profesores ON profesores.id = nivel_profesor.id_profesor
        WHERE profesores.nombre = ?
        ORDER BY niveles.nombre
    """, (profesor,))

    for (nivel,) in cursor.fetchall():
        tabla.insert("", tk.END, values=(nivel,))

    conn.close()



def asignar_nivel(profesor_var, nivel_var, tabla):
    """Asigna un nivel a un profesor."""
    profesor = profesor_var.get()
    nivel = nivel_var.get()

    if not profesor or not nivel:
        messagebox.showwarning("Advertencia", "Seleccione un profesor y un nivel.")
        return

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    # Obtener IDs
    cursor.execute("SELECT id FROM profesores WHERE nombre = ?", (profesor,))
    id_prof = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM niveles WHERE nombre = ?", (nivel,))
    id_nivel = cursor.fetchone()[0]

    # Insertar relación
    try:
        cursor.execute("""
            INSERT INTO nivel_profesor(id_nivel, id_profesor)
            VALUES (?, ?)
        """, (id_nivel, id_prof))

        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Este nivel ya está asignado a este profesor.")
    finally:
        conn.close()

    # Recargar
    cargar_niveles_de_profesor(profesor_var, tabla)



def eliminar_nivel_asignado(profesor_var, tabla):
    """Elimina una asignación nivel-profesor."""
    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Seleccione un nivel para eliminar.")
        return

    nivel = tabla.item(seleccionado)["values"][0]
    profesor = profesor_var.get()

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    # IDs
    cursor.execute("SELECT id FROM profesores WHERE nombre = ?", (profesor,))
    id_prof = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM niveles WHERE nombre = ?", (nivel,))
    id_nivel = cursor.fetchone()[0]

    cursor.execute("""
        DELETE FROM nivel_profesor
        WHERE id_profesor = ? AND id_nivel = ?
    """, (id_prof, id_nivel))

    conn.commit()
    conn.close()

    cargar_niveles_de_profesor(profesor_var, tabla)
