import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from modals import Modal


# ============================
#   CRUD PROFESORES
# ============================

def abrir_crud_profesores(parent):
    modal = Modal(
        parent=parent,
        title="Administrar Profesores",
        width=600,
        height=500
    )

    frame = modal.body

    # -------- CAMPO NOMBRE --------
    nombre_var = tk.StringVar()

    ttk.Label(frame, text="Nombre del profesor:").pack(anchor="w")
    ttk.Entry(frame, textvariable=nombre_var).pack(fill="x", pady=5)

    ttk.Button(
        frame,
        text="Agregar Profesor",
        bootstyle="success",
        command=lambda: agregar_profesor(nombre_var, tabla)
    ).pack(pady=10)

    # -------- TABLA --------
    tabla = ttk.Treeview(frame, columns=("Nombre",), show="headings", height=12)
    tabla.heading("Nombre", text="Nombre")
    tabla.column("Nombre", width=350)
    tabla.pack(fill="both", expand=True, pady=10)

    # -------- BOTONES --------
    botones = ttk.Frame(frame)
    botones.pack()

    ttk.Button(
        botones,
        text="✏️ Editar",
        bootstyle="primary",
        command=lambda: editar_profesor(tabla, parent)
    ).pack(side="left", padx=5)

    ttk.Button(
        botones,
        text="🗑️ Eliminar",
        bootstyle="danger",
        command=lambda: eliminar_profesor(tabla)
    ).pack(side="left", padx=5)

    cargar_profesores(tabla)


# ============================
#   FUNCIONES CRUD
# ============================

def agregar_profesor(nombre_var, tabla):
    nombre = nombre_var.get().strip()

    if not nombre:
        messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
        return

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO profesores(nombre) VALUES (?)", (nombre,))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Este profesor ya existe.")
    finally:
        conn.close()

    nombre_var.set("")
    cargar_profesores(tabla)


def cargar_profesores(tabla):
    tabla.delete(*tabla.get_children())

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM profesores ORDER BY nombre")

    for fila in cursor.fetchall():
        tabla.insert("", tk.END, values=fila)

    conn.close()


def eliminar_profesor(tabla):
    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Seleccione un profesor.")
        return

    nombre = tabla.item(seleccionado)["values"][0]

    if not messagebox.askyesno("Confirmar", f"¿Eliminar '{nombre}'?"):
        return

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profesores WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()

    cargar_profesores(tabla)


def editar_profesor(tabla, parent):
    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Seleccione un profesor.")
        return

    (nombre_actual,) = tabla.item(seleccionado)["values"]

    modal = Modal(
        title="Editar Profesor",
        parent=parent,
        width=400,
        height=200
    )

    frame = modal.body

    nombre_var = tk.StringVar(value=nombre_actual)

    ttk.Label(frame, text="Nombre:").pack(anchor="w")
    ttk.Entry(frame, textvariable=nombre_var).pack(fill="x", pady=5)

    ttk.Button(
        frame,
        text="Guardar",
        bootstyle="success",
        command=lambda: guardar_edicion(nombre_actual, nombre_var.get(), tabla, modal)
    ).pack(pady=10)


def guardar_edicion(original, nuevo, tabla, modal):
    nuevo = nuevo.strip()

    if not nuevo:
        messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
        return

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE profesores SET nombre=? WHERE nombre=?",
            (nuevo, original)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Ya existe un profesor con ese nombre.")
    finally:
        conn.close()

    modal.destroy()
    cargar_profesores(tabla)
