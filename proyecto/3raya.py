import sqlite3
from flask import Flask, request, jsonify, render_template, g
import datetime
import json


app = Flask(__name__)
# Configuración de SQLite
app.config['DATABASE'] = 'juego.db'

tablero = [[" " for _ in range(0, 3)] for _ in range(0, 3)]
jugador_actual = "X"
jugador1 = "X"
jugador2 = "O"
partidas_jugadas = 0


# Estadísticas de los jugadores
estadisticas_jugadores = {
    jugador1: {"victorias": 0},
    jugador2: {"victorias": 0}
}

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='juego';")
        table_exists = cursor.fetchone()
        if not table_exists:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT jugador_actual, tablero FROM juego ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            global jugador_actual
            global tablero
            if row:
                jugador_actual, tablero = row



def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
    return g.sqlite_db

# Actualizar las estadísticas después de cada juego
def actualizar_estadisticas(jugador):
    global partidas_jugadas 
    global tablero
    partidas_jugadas += 1
    estadisticas_jugadores[jugador]["victorias"] += 1
    tablero = [[" " for _ in range(0, 3)] for _ in range(0, 3)]


    # Registrar la partida en el archivo de registro
    with open('registro_partidas.txt', 'a') as file:
        file.write(f"Partida {partidas_jugadas}: Jugador {jugador} ganó.\n")


# Función para imprimir el tablero y las estadísticas de los jugadores
def obtener_tablero():
    estadisticas = {
        jugador1: estadisticas_jugadores[jugador1],
        jugador2: estadisticas_jugadores[jugador2]
    }
    return {"tablero": imprimir_tablero(), "estadisticas": estadisticas, "partidas_jugadas": partidas_jugadas}

# Función para imprimir el tablero
def imprimir_tablero():
    return tablero

# Función para verificar si alguien ha ganado
def verificar_ganador(jugador):
    for fila in tablero:
        if all(ficha == jugador for ficha in fila):
            return True
    for columna in range(3):
        if all(tablero[fila][columna] == jugador for fila in range(3)):
            return True
    if all(tablero[i][i] == jugador for i in range(0, 3)) or all(tablero[i][2 - i] == jugador for i in range(0, 3)):
        return True
    return False

@app.route('/')
def index():
    return render_template('tres_en_raya.html')

# ...

# Endpoint para obtener el estado actual del tablero
@app.route('/tablero', methods=['GET'])
def obtener_tablero_api():
    return jsonify(obtener_tablero()) 

# Endpoint para realizar un movimiento
@app.route('/mover', methods=['POST'])
def realizar_movimiento():
    global jugador_actual
    global partidas_jugadas
    global tablero

    fila = int(request.json.get('fila'))
    columna = int(request.json.get('columna'))
    for row in tablero:
        print(row)
    print(tablero)
    print(fila)
    print(columna)
    if fila is None or columna is None:
        return "Faltan datos en la solicitud", 400

    if 0 <= fila <= 2 and 0 <= columna <= 2 and tablero[fila][columna] == " ":
        tablero[fila][columna] = jugador_actual

        if verificar_ganador(jugador_actual):
            actualizar_estadisticas(jugador_actual)
            return f"¡El jugador {jugador_actual} ha ganado!", 200

        if jugador_actual == "O":
            jugador_actual = "X"
        else:
            jugador_actual = "O"

        for fila in tablero:
            for columna in range(3):
                if any(tablero[fila][columna] == " " for fila in range(3)):      
                    return "Movimiento exitoso", 200
        else:
            tablero = [[" " for _ in range(0, 3)] for _ in range(0, 3)]
            global partidas_jugadas 
            partidas_jugadas += 1
            # Registrar la partida en el archivo de registro
            with open('registro_partidas.txt', 'a') as file:
                file.write(f"Partida {partidas_jugadas}: Ambos jugadores empataron.\n")
            return "¡Es un empate!", 200
    else:
        return "Movimiento no válido. Inténtalo de nuevo.", 400
    
    # Ruta para consultar el registro de partidas
@app.route('/registro', methods=['GET'])
def consultar_registro():
    try:
        with open('registro_partidas.txt', 'r') as file:
            registro = file.readlines()
        return jsonify(registro)
    except FileNotFoundError:
        return "Registro de partidas no encontrado", 404
    
@app.route('/cargar-estado', methods=['GET'])
def obtener_estado_juego():
    print("cargado ")
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT jugador_actual, tablero FROM juego ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()

    cursor.execute('SELECT victorias1, victorias2, partidas FROM registro_partidas ORDER BY id DESC LIMIT 1')
    row2 = cursor.fetchone()
    if row:
        global tablero
        global jugador_actual
        global estadisticas_jugadores
        global partidas_jugadas
        jugador_actual, cadena_tablero = row
        estadisticas_jugadores["X"]["victorias"], estadisticas_jugadores["O"]["victorias"], partidas_jugadas = row2
        print(tablero)
        tablero = json.loads(cadena_tablero)
        print(tablero)

        return jsonify(jugador_actual, tablero, estadisticas_jugadores, partidas_jugadas)
    return jsonify(jugador_actual, tablero, estadisticas_jugadores, partidas_jugadas)

@app.route('/guardar-estado', methods=['GET'])
def guardar_estado_juego():
    print("guardado ")
    global jugador_actual
    global tablero
    global estadisticas_jugadores
    global partidas_jugadas

    db = get_db()
    cursor = db.cursor()
    cadena = json.dumps(tablero)
    print(cadena)
    cursor.execute('INSERT INTO juego (jugador_actual, tablero) VALUES (?, ?)',
                   (jugador_actual, cadena))
    db.commit()
    
    cursor.execute('INSERT INTO registro_partidas (victorias1, victorias2, partidas) VALUES (?, ?, ?)',
                   (estadisticas_jugadores["X"]["victorias"],estadisticas_jugadores["O"]["victorias"], partidas_jugadas))
    db.commit()

    return jsonify(obtener_tablero())


if __name__ == "__main__":
    init_db()
    app.run()