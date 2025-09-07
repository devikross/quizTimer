import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class QuizUI:
    def __init__(self):
        self.root = tk.Tk()
        
        self.root.title("Quiz")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()
        
        self.carpetaImg = "imagenes\\"
        
        self.lbl_img = tk.Label(self.root, bg="black")
        self.lbl_img.pack(pady=(30,10))

        self.lbl = tk.Label(
            self.root, text="", font=("Arial", 22, "bold"),
            fg="white", bg="black", wraplength=1000, justify="center"
        )
        self.lbl.pack(pady=20)

        self.frame = tk.Frame(self.root, bg="black")
        self.frame.pack(pady=20)

        self.botones = []
        for i in range(4):
            btn = tk.Button(
                self.frame,
                text="",
                font=("Arial", 24),
                wraplength=200,
                justify="center",
                compound="top",
                bg="black",
                fg="#b3def3",
                activebackground="black",
                borderwidth=0,
                highlightthickness=0
            )

            btn.bind("<Enter>", lambda e, b=btn: b.config(fg="#e6f4fb", bg="#222222"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg="#b3def3", bg="black"))

            btn.grid(row=i//2, column=i%2, padx=40, pady=40, sticky="nsew")
            self.botones.append(btn)

        self.callback = None

    def mostrar_pregunta(self, pregunta, opciones_barajadas, indice=None, total=None):
        texto = pregunta.get("pregunta", "")
        if indice is not None and total is not None:
            texto = f"Pregunta {indice+1} de {total}\n\n{texto}"
        self.lbl.config(text=texto)

        if pregunta.get("img_pregunta"):
            img = Image.open(self.carpetaImg + pregunta.get("img_pregunta"))
            factor = 300 / img.height
            img = img.resize((int(img.width * factor), 300), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(img)
            self.lbl_img.config(image=imgtk)
            self.lbl_img.image = imgtk
        else:
            self.lbl_img.config(image="")
            self.lbl_img.image = None

        for i, (idx_original, opt) in enumerate(opciones_barajadas):
            ruta_img = None
            if pregunta.get("img_opciones"):
                ruta_img = pregunta["img_opciones"][idx_original]

            if ruta_img:
                img = Image.open(self.carpetaImg + ruta_img)
                factor = 150 / img.height
                img = img.resize((int(img.width * factor), 150), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(img)
                self.botones[i].config(
                    image=imgtk, text=opt, compound="top"
                )
                self.botones[i].image = imgtk
            else:
                self.botones[i].config(text=opt, image="", compound="none")
                self.botones[i].image = None

            self.botones[i].config(state="normal")
            if self.callback:
                self.botones[i].config(command=lambda i=i: self.callback(i))
            self.botones[i].grid()

    def mostrar_feedback(self, texto):
        self.lbl.config(text=texto)
        for btn in self.botones:
            btn.grid_remove()

    def registrar_callback(self, func):
        self.callback = func

    def mostrar_resultado(self, tiempo_anadido):
        messagebox.showinfo("Resultado", f"Tiempo añadido total: {tiempo_anadido} segundos")

    def iniciar(self):
        self.root.mainloop()
