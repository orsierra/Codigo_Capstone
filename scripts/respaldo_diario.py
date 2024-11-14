import logging
import sqlite3
import pandas as pd
from datetime import datetime
import os
import time

# Configuración de logging
logging.basicConfig(filename="C:\\Users\\GOLDEN GAMERS\\Desktop\\Capstone\\Codigo_Capstone\\scripts\\respaldo_log.txt",
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Iniciando el script de respaldo diario.")

# Ruta de la base de datos
db_path = "C:\\Users\\GOLDEN GAMERS\\Desktop\\Capstone\\Codigo_Capstone\\db.sqlite3"

# Intentar conectar a la base de datos hasta 3 veces en caso de error
max_attempts = 3
conn = None

for attempt in range(max_attempts):
    try:
        conn = sqlite3.connect(db_path)
        logging.info("Conectado a la base de datos.")
        break
    except Exception as e:
        logging.error("Error al conectar a la base de datos: %s", e)
        if attempt < max_attempts - 1:
            logging.info("Reintentando conexión...")
            time.sleep(5)  # Espera 5 segundos antes de reintentar
        else:
            logging.error("No se pudo conectar a la base de datos después de varios intentos.")
            exit()

# Si la conexión fue exitosa, proceder con el respaldo
if conn:
    # Obtener todas las tablas de la base de datos que comienzan con "core_"
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'core_%';")
        tables = cursor.fetchall()
        logging.info("Tablas obtenidas: %s", tables)
    except Exception as e:
        logging.error("Error al obtener tablas: %s", e)
        conn.close()
        exit()

    # Solo proceder si hay tablas en la base de datos
    if tables:
        # Ruta de respaldo
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        backup_dir = "C:\\Users\\GOLDEN GAMERS\\Desktop\\Capstone\\Codigo_Capstone\\scripts\\backups"
        os.makedirs(backup_dir, exist_ok=True)
        excel_path = os.path.join(backup_dir, f"respaldo_{fecha_actual}.xlsx")

        # Exportar cada tabla que empiece con "core_" a una hoja de Excel
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                for table_name, in tables:
                    # Limitar el nombre de la hoja a 31 caracteres
                    sheet_name = table_name[:31]
                    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    df.to_excel(writer, sheet_name=sheet_name, index=False, na_rep="")
            logging.info("Respaldo diario guardado en %s", excel_path)
        except Exception as e:
            logging.error("Error al exportar datos a Excel: %s", e)
    else:
        logging.info("No se encontraron tablas en la base de datos con el prefijo 'core_'. No se generó el respaldo.")

    # Cerrar la conexión
    conn.close()
    logging.info("Conexión cerrada.")
