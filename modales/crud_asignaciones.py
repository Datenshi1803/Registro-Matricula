import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from modals import Modal


# ============================
#  ASIGNAR ASIGNATURAS A PROFESORES
# ============================

def abrir_asignacion_profesor_asignaturas(parent):
    modal = Modal(
        parent=parent,
        title="Asignar Asignaturas a Profesores",
        width=650,
        height=520
    )

    frame = modal.body

    # Seleccionar profesor
    ttk.Label(frame, text="Seleccione Profesor:", font=("Segoe UI", 11, "bold")).pack(anchor="w")
    profesor_var = tk.StringVar()
    cb_prof = ttk.Combobox(frame, textvariable=profesor_var, state="readonly", width=40)
    cb_prof.pack(fill="x", pady=5)

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM profesores ORDER BY nombre")
    cb_prof["values"] = [p[0] for p in cursor.fetchall()]
    conn.close()

    # Tabla
    ttk.Label(frame, text="Asignaturas del profesor:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=10)

    tabla = ttk.Treeview(frame, columns=("Asignatura",), show="headings", height=10)
    tabla.heading("Asignatura", text="Asignatura")
    tabla.column("Asignatura", width=320)
    tabla.pack(fill="both", expand=True)

    # Asignar
    ttk.Label(frame, text="Asignar nueva asignatura:").pack(anchor="w")
    asig_var = tk.StringVar()
    cb_asig = ttk.Combobox(frame, textvariable=asig_var, state="readonly", width=40)
    cb_asig.pack(fill="x", pady=5)

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM asignaturas ORDER BY nombre")
    cb_asig["values"] = [a[0] for a in cursor.fetchall()]
    conn.close()

    ttk.Button(
        frame,
        text="➕ Asignar",
        bootstyle="success",
        command=lambda: asignar_asignatura(profesor_var, asig_var, tabla)
    ).pack(pady=10)

    ttk.Button(
        frame,
        text="🗑️ Eliminar Selección",
        bootstyle="danger",
        command=lambda: eliminar_asignacion(profesor_var, tabla)
    ).pack()

    cb_prof.bind("<<ComboboxSelected>>", lambda e: cargar_asignaciones_profesor(profesor_var, tabla))


def cargar_asignaciones_profesor(profesor_var, tabla):
    tabla.delete(*tabla.get_children())

    profesor = profesor_var.get()
    if not profesor:
        return

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT asignaturas.nombre
        FROM asignaturas
        JOIN profesor_asignatura ON asignaturas.id = profesor_asignatura.id_asignatura
        JOIN profesores ON profesores.id = profesor_asignatura.id_profesor
        WHERE profesores.nombre = ?
        ORDER BY asignaturas.nombre
    """, (profesor,))

    for (asig,) in cursor.fetchall():
        tabla.insert("", tk.END, values=(asig,))

    conn.close()


def asignar_asignatura(profesor_var, asignatura_var, tabla):
    profesor = profesor_var.get()
    asignatura = asignatura_var.get()

    if not profesor or not asignatura:
        messagebox.showwarning("Advertencia", "Seleccione un profesor y una asignatura.")
        return

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM profesores WHERE nombre=?", (profesor,))
    id_prof = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM asignaturas WHERE nombre=?", (asignatura,))
    id_asig = cursor.fetchone()[0]

    try:
        cursor.execute("INSERT INTO profesor_asignatura(id_profesor, id_asignatura) VALUES (?,?)",
                       (id_prof, id_asig))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Esta asignatura ya está asignada.")

    conn.close()

    cargar_asignaciones_profesor(profesor_var, tabla)


def eliminar_asignacion(profesor_var, tabla):
    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Seleccione una asignatura para eliminar.")
        return

    asignatura = tabla.item(seleccionado)["values"][0]
    profesor = profesor_var.get()

    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM profesores WHERE nombre=?", (profesor,))
    id_prof = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM asignaturas WHERE nombre=?", (asignatura,))
    id_asig = cursor.fetchone()[0]

    cursor.execute("DELETE FROM profesor_asignatura WHERE id_profesor=? AND id_asignatura=?",
                   (id_prof, id_asig))
    conn.commit()
    conn.close()

    cargar_asignaciones_profesor(profesor_var, tabla)
