from flask import Flask, Response, request
import pymysql
import json
import os

app = Flask(__name__)

# TOKEN
TOKEN = "profe123"

# Conexión a Railway MySQL
def get_connection():
    return pymysql.connect(
        host="caboose.proxy.rlwy.net",
        port=48033,
        user="root",
        password="WCgIxNYZwDigbFRCaOsXANJOTHyBVAUl",
        database="railway",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def index():
    token = request.args.get("token")

    # 🔐 Validar token
    if token != TOKEN:
        return {"error": "No autorizado"}, 401

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        u.id as universidad_id,
        u.nombre as universidad,
        u.tipo_institucion,
        u.modalidad,
        c.nombre as ciudad,
        e.nombre as estado,
        ca.nombre as carrera
    FROM universidades u
    JOIN ciudades c ON u.ciudad_id = c.id
    JOIN estados e ON c.estado_id = e.id
    LEFT JOIN universidad_carreras uc ON u.id = uc.universidad_id
    LEFT JOIN carreras ca ON uc.carrera_id = ca.id
    ORDER BY u.nombre
    """

    cursor.execute(query)
    resultados = cursor.fetchall()
    conn.close()

    universidades = {}

    for fila in resultados:
        uid = fila["universidad_id"]

        if uid not in universidades:
            universidades[uid] = {
                "nombre": fila["universidad"],
                "ciudad": fila["ciudad"],
                "estado": fila["estado"],
                "tipo": fila["tipo_institucion"],
                "modalidad": fila["modalidad"],
                "carreras": []
            }

        if fila["carrera"]:
            universidades[uid]["carreras"].append(fila["carrera"])

    return Response(
        json.dumps(list(universidades.values()), indent=4, ensure_ascii=False),
        mimetype="application/json"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)