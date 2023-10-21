CREATE TABLE juego (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jugador_actual TEXT,
    tablero TEXT
);

CREATE TABLE registro_partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    victorias1 INTEGER,
    victorias2 INTEGER,
    partidas INTEGER
);