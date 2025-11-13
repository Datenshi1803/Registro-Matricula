import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from modals import Modal


# ============================
#   CRUD ASIGNATURAS
# ============================

def abrir_crud_asignaturas(parent):
    modal = Modal(
        parent=parent,
        title="Administrar Asignaturas",
        width=500,
        height=450
    )

    frame = modal.body

    asig_var = tk.StringVar()
    ttk.Label(frame, text="Nombre de la asignatura:").pack(anchor="w")
    ttk.Entry(frame, textvariable=asig_var).pack(fill="x", pady=5)

    ttk.Button(
        frame,
        text="Agregar Asignatura",
        bootstyle="success",
        command=lambda: agregar_asignatura(asig_var, tabla)
    ).pack(pady=10)

    tabla = ttk.Treeview(frame, columns=("Asignatura",), show="headings", height=12)
    tabla.heading("Asignatura", text="Asignatura")
    tabla.column("Asignatura", width=350)
    tabla.pack(fill="both", expand=True)

    botones = ttk.Frame(frame)
    botones.pack()

    ttk.Button(botones, text="✏️ Editar", bootstyle="primary",
               command=lambda: editar_asignatura(tabla)).pack(side="left", padx=5)

    ttk.Button(botones, text="🗑️ Eliminar", bootstyle="danger",
               command=lambda: eliminar_asignatura(tabla)).pack(side="left", padx=5)

    cargar_asignaturas(tabla)


def agregar_asignatura(asig_var, tabla):
    nombre = asig_var.get().strip()
    if not nombre:
        messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
        return

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO asignaturas(nombre) VALUES (?)", (nombre,))
        conn.commit()
        asig_var.set("")
        cargar_asignaturas(tabla)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "La asignatura ya existe.")

    conn.close()


def cargar_asignaturas(tabla):
    tabla.delete(*tabla.get_children())
    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM asignaturas ORDER BY nombre")

    for (nombre,) in cursor.fetchall():
        tabla.insert("", tk.END, values=(nombre,))

    conn.close()


def eliminar_asignatura(tabla):
    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Seleccione una asignatura.")
        return

    nombre = tabla.item(seleccionado)["values"][0]

    if not messagebox.askyesno("Confirmar", f"¿Eliminar '{nombre}'?"):
        return

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM asignaturas WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()

    cargar_asignaturas(tabla)


def editar_asignatura(tabla):
    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Seleccione una asignatura.")
        return

    nombre_actual = tabla.item(seleccionado)["values"][0]

    modal = Modal(title="Editar Asignatura", parent=tabla, width=400, height=200)
    frame = modal.body

    nombre_var = tk.StringVar(value=nombre_actual)

    ttk.Label(frame, text="Nuevo nombre:").pack(anchor="w")
    ttk.Entry(frame, textvariable=nombre_var).pack(fill="x")

    ttk.Button(
        frame,
        text="Guardar Cambios",
        bootstyle="success",
        command=lambda: guardar_edicion(nombre_actual, nombre_var.get(), tabla, modal)
    ).pack(pady=10)


def guardar_edicion(original, nuevo, tabla, modal):
    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE asignaturas SET nombre=? WHERE nombre=?", (nuevo, original))
    conn.commit()
    conn.close()

    modal.destroy()
    cargar_asignaturas(tabla)
