from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
# Aunque no se usa para sesiones, Flask lo requiere para otras funciones internas como `flash` si se usara.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'una_clave_secreta_muy_larga_y_aleatoria_para_desarrollo')

# Eliminamos la cadena de conexión a la base de datos ya que no se guardarán los cálculos.
# DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
# print(f"DB_CONNECTION_STRING cargada: {DB_CONNECTION_STRING}")

# Eliminamos la función de conexión a la base de datos.
# def get_db_connection():
#     conn = None
#     try:
#         conn = pyodbc.connect(DB_CONNECTION_STRING)
#     except pyodbc.Error as ex:
#         sqlstate = ex.args[0]
#         print(f"Error de conexión a la base de datos: {sqlstate}")
#     return conn

@app.route("/")
def home():
    # Renderizamos la plantilla principal sin pasar ningún dato de usuario.
    return render_template("index.html")

# Eliminamos las rutas de registro y autenticación.
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     # ... código de registro ...
#     pass

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     # ... código de login ...
#     pass

# @app.route("/logout")
# def logout():
#     # ... código de logout ...
#     pass

@app.route("/calculate_and_save_carbon", methods=["POST"])
def calculate_carbon():
    # Eliminamos cualquier referencia a user_id o sesión.

    try:
        factor = float(request.form["transporte"])
        km = float(request.form["kilometros"])
    except ValueError:
        return jsonify({"success": False, "message": "Valores de entrada inválidos."}), 400

    if km < 0:
        return jsonify({"success": False, "message": "Ingresa una distancia válida."}), 400

    huella = factor * km
    recomendacion = ""

    if huella == 0:
        recomendacion = "¡Excelente! No generas emisiones con tu medio de transporte actual."
    elif huella <= 3:
        recomendacion = "Sigue optando por transporte público o compártelo para reducir más tu huella."
    elif huella <= 10:
        recomendacion = "Considera caminar, usar bicicleta o transporte público algunos días de la semana."
    else:
        recomendacion = "Tu huella es alta. Cambiar el uso del automóvil por alternativas sostenibles tendría un gran impacto."

    # Eliminamos toda la lógica de guardado en la base de datos.
    # user_id = 1
    # conn = get_db_connection()
    # if conn:
    #     cursor = conn.cursor()
    #     try:
    #         cursor.execute(
    #             "INSERT INTO CarbonFootprintCalculations (UserID, WeeklyCO2, Recommendations) VALUES (?, ?, ?)",
    #             (user_id, huella, recomendacion)
    #         )
    #         conn.commit()
    #         conn.close()
    #         return jsonify({
    #             "success": True,
    #             "huella": f"{huella:.2f}",
    #             "recomendacion": recomendacion
    #         })
    #     except Exception as e:
    #         conn.close()
    #         return jsonify({"success": False, "message": f"Error al guardar el cálculo: {e}"}), 500
    # else:
    #     return jsonify({"success": False, "message": "Fallo la conexión a la base de datos."}), 500

    # Retornamos solo el cálculo y la recomendación.
    return jsonify({
        "success": True,
        "huella": f"{huella:.2f}",
        "recomendacion": recomendacion
    })

if __name__ == "__main__":
    app.run(debug=True)