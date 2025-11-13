import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from modals import Modal

def abrir_crud_niveles(parent):
    modal = Modal(
        parent=parent,
        title="Administrar Niveles",
        width=500,
        height=450
    )

    frame = modal.body

    nivel_var = tk.StringVar()
    ttk.Label(frame, text="Nuevo Nivel:").pack(anchor="w")
    ttk.Entry(frame, textvariable=nivel_var).pack(fill="x", pady=5)

    tabla = ttk.Treeview(frame, columns=("Nivel",), show="headings", height=12)
    tabla.heading("Nivel", text="Nivel")
    tabla.column("Nivel", width=300)
    tabla.pack(fill="both", expand=True, pady=10)

    ttk.Button(
        frame, text="Agregar Nivel",
        bootstyle="success",
        command=lambda: agregar_nivel(nivel_var, tabla)
    ).pack(pady=5)

    ttk.Button(
        frame,
        text="🗑️ Eliminar Seleccionado",
        bootstyle="danger",
        command=lambda: eliminar_nivel(tabla)
    ).pack()

    cargar_niveles(tabla)

def cargar_niveles(tabla):
    tabla.delete(*tabla.get_children())
    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM niveles ORDER BY nombre")
    for (nombre,) in cursor.fetchall():
        tabla.insert("", tk.END, values=(nombre,))
    conn.close()

def agregar_nivel(nivel_var, tabla):
    nombre = nivel_var.get().strip()
    if not nombre:
        messagebox.showwarning("Advertencia", "Ingrese un nombre de nivel.")
        return

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO niveles(nombre) VALUES (?)", (nombre,))
        conn.commit()
        nivel_var.set("")
        cargar_niveles(tabla)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El nivel ya existe.")
    conn.close()

def eliminar_nivel(tabla):
    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Seleccione un nivel para eliminar.")
        return

    nivel = tabla.item(seleccionado)["values"][0]

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM niveles WHERE nombre = ?", (nivel,))
    conn.commit()
    conn.close()

    cargar_niveles(tabla)
