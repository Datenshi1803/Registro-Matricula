# modals.py
import ttkbootstrap as ttk

class Modal(ttk.Toplevel):
    def __init__(self, parent, title="Ventana", width=500, height=400):
        super().__init__(parent)

        self.title(title)
        self.geometry(f"{width}x{height}+{parent.winfo_x()+50}+{parent.winfo_y()+50}")
        self.transient(parent)      # Se comporta como modal
        self.grab_set()             # Bloquea la ventana principal
        self.resizable(False, False)

        # Frame donde irán los widgets
        self.body = ttk.Frame(self, padding=15)
        self.body.pack(expand=True, fill="both")
