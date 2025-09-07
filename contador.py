import tkinter as tk
import subprocess, sys

class ContadorApp:
    def __init__(self, root, segundos):
        self.root = root
        self.root.title("Tiempo de juego")

        ancho, alto = 200, 100
        x = root.winfo_screenwidth() - ancho - 20
        y = root.winfo_screenheight() - alto - 60
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

        self.root.configure(bg="black")
        self.root.overrideredirect(True)       # sin barra
        self.root.attributes("-topmost", True) # siempre encima
        self.root.attributes("-alpha", 0.85)   # semitransparente

        self.segundos = segundos

        self.label = tk.Label(root, text="", font=("Arial", 28, "bold"),
                              fg="lime", bg="black")
        self.label.pack(expand=True)

        self.actualizar()

    def actualizar(self):
        if self.segundos >= 0:
            m, s = divmod(self.segundos, 60)
            self.label.config(text=f"{m:02d}:{s:02d}")
            self.segundos -= 1
            self.root.after(1000, self.actualizar)
        else:
            self.root.destroy()
            subprocess.Popen([sys.executable, "main.py"])

if __name__ == "__main__":
    minutos = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    root = tk.Tk()
    app = ContadorApp(root, minutos)
    root.mainloop()
