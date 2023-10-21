CREATE TABLE juego (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jugador_actual TEXT,
    tablero TEXT
);

CREATE TABLE registro_partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jugador_ganador TEXT,
    fecha_ganada TIMESTAMP
);