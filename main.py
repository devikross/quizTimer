from interfaz import QuizUI
import json, os, random, subprocess, sys

STATS_FILE = "stats.json"
correcto_msgs = [
    "¡Fantástico!",
    "¡Excelente!",
    "¡De locos!",
    "¡Durísimo!",
    "¡Crack total!",
    "¡La rompiste!",
]

incorrecto_msgs = [
    "Ups... la cagaste",
    "Nooooo la politziaaaa",
    "Se cayó el server",
    "¡Error 404 en tu cerebro!",
    "Ñeee, sigue intentando",
]

with open("preguntas.json", "r", encoding="utf-8") as f:
    preguntas = json.load(f)

if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)
else:
    stats = {}

ui = QuizUI()
indice = 0
tiempo_anadido = 0
seleccionadas = []
opciones_barajadas = []

def preparar_opciones(pregunta):
    opciones = list(enumerate(pregunta["opciones"]))
    random.shuffle(opciones)
    return opciones

def seleccionar_numero(n):
    global num_preguntas
    num_preguntas = n
    iniciar_quiz()

def mostrar_pantalla_inicial():
    ui.lbl.config(text="Selecciona el número de preguntas")
    ui.lbl_img.config(image="")
    for i, n in enumerate([5,10,20,30]):
        ui.botones[i].config(text=str(n), state="normal",
                             command=lambda n=n: seleccionar_numero(n))
        ui.botones[i].grid()
    for i in range(4, len(ui.botones)):
        ui.botones[i].grid_remove()

def iniciar_quiz():
    global seleccionadas, indice, opciones_barajadas
    pesos = []
    for p in preguntas:
        key = p["pregunta"]
        info = stats.get(key, {"intentos":0,"aciertos":0})
        intentos, aciertos = info["intentos"], info["aciertos"]
        if intentos == 0:
            peso = 10
        else:
            peso = 1 + (intentos - aciertos)
            if peso < 1:
                peso = 1
        pesos.append(peso)
    
    seleccionadas[:] = random.choices(preguntas, weights=pesos, k=num_preguntas)
    indice = 0
    opciones_barajadas[:] = preparar_opciones(seleccionadas[indice])
    mostrar_pregunta_actual()

def mostrar_pregunta_actual():
    ui.mostrar_pregunta(seleccionadas[indice], opciones_barajadas, indice, num_preguntas)

def verificar(eleccion):
    global indice, tiempo_anadido, opciones_barajadas

    p = seleccionadas[indice]
    idx_original = opciones_barajadas[eleccion][0]
    correcto = idx_original == p["respuesta"]

    if correcto:
        tiempo_anadido += p.get("dificultad",1) * 30
        ui.mostrar_feedback(f"\n\n\n✅ {random.choice(correcto_msgs)}\n\n{p.get('feedback','')}")
        delay = 1500
    else:
        ui.mostrar_feedback(f"\n\n\n❌ {random.choice(incorrecto_msgs)}\n\n{p.get('feedback','')}")
        delay = 10000

    key = p["pregunta"]
    if key not in stats:
        stats[key] = {"intentos":0, "aciertos":0}
    stats[key]["intentos"] += 1
    if correcto:
        stats[key]["aciertos"] += 1
    with open(STATS_FILE,"w",encoding="utf-8") as f:
        json.dump(stats,f,indent=2,ensure_ascii=False)

    ui.root.after(delay, siguiente_pregunta)

def siguiente_pregunta():
    global indice, opciones_barajadas
    indice += 1
    if indice < len(seleccionadas):
        opciones_barajadas = preparar_opciones(seleccionadas[indice])
        mostrar_pregunta_actual()
    else:
        ui.mostrar_resultado(tiempo_anadido)
        ui.root.destroy()
        subprocess.Popen([sys.executable, "contador.py", str(tiempo_anadido)])

ui.registrar_callback(verificar)
mostrar_pantalla_inicial()
ui.iniciar()