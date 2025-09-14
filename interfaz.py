import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import pygame

class QuizUI:
    def __init__(self):
        self.root = tk.Tk()
        
        self.colores = ["white","#f7d6ac","#e1f7ac","#acf7eb","#f7acf3"]
        self.coloresBu = self.colores[:]
        
        self.root.title("Quiz")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()
        
        self.carpetaImg = "imagenes/"
        self.carpetaAudio = "audios/"
        
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
        for i in range(10):
            btn = tk.Button(
                self.frame,
                text="",
                font=("Arial", 26),
                wraplength=400,
                justify="center",
                compound="top",
                bg="black",
                fg="#b3def3",
                borderwidth=0,
                highlightthickness=0
            )

            self.enter_leave(btn)

            btn.grid(row=i//2, column=i%2, padx=40, pady=40, sticky="nsew")
            self.botones.append(btn)

        self.callback = None

    def enter_leave(self, btn):
        btn.bind("<Enter>", lambda e, b=btn: b.config(fg="#e6f4fb", bg="#222222"))
        btn.bind("<Leave>", lambda e, b=btn: b.config(fg="#b3def3", bg="black"))
    
    def reestablecer_colores(self):
        for btn in self.botones:
            btn.config(fg="#b3def3", bg="black")
            self.enter_leave(btn)
        self.colores = self.coloresBu[:]
    
    def colorear(self, eleccion, lrel=-1):
        if lrel == -1:
            self.enter_leave(self.botones[eleccion])
            colorRef = self.botones[eleccion].cget("bg")
            self.botones[eleccion].config(fg="#b3def3", bg="black")
            for i,btn in enumerate(self.botones):
                if btn.cget("bg") == colorRef:
                    self.colores.append(colorRef)
                    btn.config(fg="#b3def3", bg="black")
                    return i
        else:
            self.botones[eleccion].config(fg="black", bg=self.colores[0:1][0])
            self.botones[eleccion].unbind("<Enter>")
            self.botones[eleccion].unbind("<Leave>")
            if lrel%2 != 0:
                self.colores.pop(0)
        return -1

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
            
        if pregunta.get("tipo") == "relation":
            a,b = opciones_barajadas
            for i in range(10):
                if i%2 == 0:
                    text = a[i//2][1]
                else:
                    text = b[i//2][1]
                self.botones[i].config(text=text, image="", compound="none")
                self.botones[i].image = None
                self.botones[i].config(state="normal")
                
                if self.callback:
                    self.botones[i].config(command=lambda i=i: self.callback(i))

                self.botones[i].grid()
            return

        for i, (idx_original, opt) in enumerate(opciones_barajadas):
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
        
        if pregunta.get("audio"):
            audio_path = self.carpetaAudio + pregunta.get("audio")
            if os.path.exists(audio_path):
                pygame.mixer.init()
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()

    def mostrar_feedback(self, texto, pregunta, audio = False):
        for btn in self.botones:
            btn.grid_remove()
        self.lbl.config(text=texto)
        if pregunta.get("audio") and audio:
            audio_path = self.carpetaAudio + pregunta.get("audio")
            nombre, ext = os.path.splitext(audio_path)
            feed_path = nombre + "_feed" + ext            
            if os.path.exists(feed_path):
                pygame.mixer.init()
                pygame.mixer.music.load(feed_path)
                pygame.mixer.music.play()

    def registrar_callback(self, func):
        self.callback = func

    def mostrar_mensaje(self, mensaje):
        messagebox.showinfo("Resultado", mensaje)

    def iniciar(self):
        self.root.mainloop()
