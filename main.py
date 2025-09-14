from interfaz import QuizUI
import json, os, random, subprocess, sys

STATS_FILE = "stats.json"
correcto_msgs = [
    "¡Fantástico!",
    "¡Excelente!",
    "¡De locos!",
    "¡Durísimo!",
    "¡Crack total!",
]

incorrecto_msgs = [
    "Ups...",
    "Nooooo la politziaaaa",
    "Se cayó el server",
    "¡Error 404!",
    "Sigue intentando",
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
seguida = 0
tiempo_anadido = 0
seleccionadas = []
opciones_barajadas = []
relacionadas = []

def preparar_opciones(pregunta):
    opciones = list(enumerate(pregunta["opciones"]))
    random.shuffle(opciones)
    if pregunta.get("tipo") == "relation":
        relaciones = list(enumerate(pregunta["opciones"].values()))
        random.shuffle(relaciones)
        return opciones, relaciones
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

def muestrear(preguntas, pesos, k):
    items, w = preguntas[:], pesos[:]
    muestra = []
    for _ in range(min(k, len(items))):
        elegido = random.choices(items, weights=w, k=1)[0]
        i = items.index(elegido)
        muestra.append(items.pop(i))
        w.pop(i)
    return muestra

def iniciar_quiz():
    global seleccionadas, indice, opciones_barajadas
    pesos = []
    for p in preguntas:
        key = p["pregunta"]
        info = stats.get(key, {"intentos":0,"aciertos":0})
        intentos, aciertos = int(info["intentos"]), int(info["aciertos"])
        peso = 10 if intentos == 0 else max(1, 1 + (intentos - aciertos))
        pesos.append(peso)
    
    seleccionadas[:] = muestrear(preguntas, pesos, num_preguntas)
    indice = 0
    opciones_barajadas[:] = preparar_opciones(seleccionadas[indice])
    mostrar_pregunta_actual()

def mostrar_pregunta_actual():
    ui.mostrar_pregunta(seleccionadas[indice], opciones_barajadas, indice, num_preguntas)

def verificar(eleccion):
    global indice, tiempo_anadido, opciones_barajadas, seguida, relacionadas
    
    delay = 0
    
    pregunta = seleccionadas[indice]
    correcto = False
    
    if pregunta.get("tipo") == "relation":
        if relacionadas:
            if eleccion in relacionadas:
                eliminar = ui.colorear(eleccion)
                relacionadas.remove(eleccion)
                if eliminar != -1:
                    relacionadas.remove(eliminar)
            elif relacionadas[-1:][0]%2 == 0 and eleccion%2 != 0:
                relacionadas.append(eleccion)
                ui.colorear(eleccion,len(relacionadas)-1)
            elif relacionadas[-1:][0]%2 == 0 and eleccion%2 == 0:
                ui.colorear(relacionadas.pop())
                relacionadas.append(eleccion)
                ui.colorear(eleccion,len(relacionadas)-1)
            elif relacionadas[-1:][0]%2 != 0 and eleccion%2 == 0:
                relacionadas.append(eleccion)
                ui.colorear(eleccion,len(relacionadas)-1)
            if len(relacionadas) == 10:
                ui.reestablecer_colores()
                opciones_correctas = 0
                feedback_relacion = ""
                while(relacionadas):
                    parteB = int((relacionadas.pop()-1)/2)
                    parteA = int(relacionadas.pop()/2)
                    a,b = opciones_barajadas
                    if a[parteA][0] == b[parteB][0]:
                        opciones_correctas += 1
                    else:
                        indice = next(num for num, comparador in a if comparador == a[parteA][1])
                        valor = next(comparador for num, comparador in b if num == indice)  
                        feedback_relacion += f"'{a[parteA][1]}' -----> {valor}\n\n"
                if opciones_correctas == 5:
                    seguida += 1
                    correcto = True
                    tiempo_anadido += pregunta.get("dificultad",1) * 150
                    ui.mostrar_feedback(f"\n\n\n\n\n\n\n\n\n✅ {random.choice(correcto_msgs)}",seleccionadas[indice])
                    delay = 1000
                elif opciones_correctas >= 3:
                    tiempo_anadido += pregunta.get("dificultad",1) * opciones_correctas * 25
                    ui.mostrar_feedback(f"\n\nLa relación correcta es:\n\n {feedback_relacion}",pregunta)
                    delay = 10000
                else:
                    seguida = 0
                    tiempo_anadido += pregunta.get("dificultad",1) * opciones_correctas * 10
                    ui.mostrar_feedback(f"\n\n\n❌ {random.choice(incorrecto_msgs)}\n\n\nTe daré algo de tiempo para que veas la relación correcta:\n\n{feedback_relacion}",pregunta)
                    delay = 20000
            else:
                return
        else:
            if eleccion%2 == 0:
                relacionadas.append(eleccion)
                ui.colorear(eleccion,len(relacionadas)-1)
            return
    else:
        idx_original = opciones_barajadas[eleccion][0]
        correcto = idx_original == pregunta["respuesta"]
        if correcto:
            seguida += 1
            tiempo_anadido += pregunta.get("dificultad",1) * 30
            ui.mostrar_feedback(f"\n\n\n\n\n\n\n\n\n✅ {random.choice(correcto_msgs)}",seleccionadas[indice])
            delay = 1000
        else:
            seguida = 0
            ui.mostrar_feedback(f"\n\n\n❌ {random.choice(incorrecto_msgs)}\n\n{pregunta.get('feedback','')}",seleccionadas[indice],True)
            delay = 15000
        
    if seguida >= 5:
        ui.mostrar_mensaje("Has contestado bien 5 preguntas de opción múltiple de seguido, por eso tienes 2 minutos extra")
        seguida = 0
        tiempo_anadido += 120
        
    key = pregunta["pregunta"]
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
        ui.mostrar_mensaje(f"Tiempo añadido: {tiempo_anadido} segundos")
        ui.root.destroy()
        subprocess.Popen([sys.executable, "contador.py", str(tiempo_anadido)])

ui.registrar_callback(verificar)
mostrar_pantalla_inicial()
ui.iniciar()




