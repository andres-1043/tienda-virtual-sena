from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

app.secret_key = "tienda_sena_2026"


# =========================
# PRODUCTOS
# =========================

productos = {
    1: {
        "nombre": "Cuaderno",
        "precio": 8000,
        "emoji": "📓"
    },
    2: {
        "nombre": "Lápiz",
        "precio": 1500,
        "emoji": "✏️"
    },
    3: {
        "nombre": "Colores",
        "precio": 12000,
        "emoji": "🖍️"
    },
    4: {
        "nombre": "Regla",
        "precio": 2500,
        "emoji": "📐"
    }
}


# =========================
# BASE DE DATOS
# =========================

def crear_base_datos():

    conexion = sqlite3.connect("pedidos.db")

    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            curso TEXT NOT NULL,
            correo TEXT NOT NULL,
            telefono TEXT NOT NULL,
            total INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            metodo_pago TEXT NOT NULL
    )
""")
    conexion.commit()

    conexion.close()


crear_base_datos()

# =========================
# ACTUALIZAR BASE DE DATOS
# =========================

def actualizar_base_datos():

    conexion = sqlite3.connect("pedidos.db")
    cursor = conexion.cursor()

    cursor.execute("PRAGMA table_info(pedidos)")

    columnas = [columna[1] for columna in cursor.fetchall()]

    if "metodo_pago" not in columnas:

        cursor.execute("""
            ALTER TABLE pedidos
            ADD COLUMN metodo_pago TEXT NOT NULL DEFAULT 'Efectivo en el colegio'
        """)

    conexion.commit()
    conexion.close()


actualizar_base_datos()

# =========================
# PÁGINA PRINCIPAL
# =========================

@app.route("/")
def inicio():
    return render_template("index.html")


# =========================
# AGREGAR AL CARRITO
# =========================

@app.route("/agregar/<int:id>")
def agregar(id):

    carrito = session.get("carrito", {})

    if not isinstance(carrito, dict):
        carrito = {}

    id = str(id)

    if int(id) in productos:
        carrito[id] = carrito.get(id, 0) + 1

    session["carrito"] = carrito
    session.modified = True

    return redirect(url_for("carrito"))


# =========================
# AUMENTAR CANTIDAD
# =========================

@app.route("/aumentar/<int:id>")
def aumentar(id):

    carrito = session.get("carrito", {})

    carrito = {
        str(clave): valor
        for clave, valor in carrito.items()
    }

    id = str(id)

    if id in carrito:
        carrito[id] += 1

    session["carrito"] = carrito

    return redirect(url_for("carrito"))


# =========================
# DISMINUIR CANTIDAD
# =========================

@app.route("/disminuir/<int:id>")
def disminuir(id):

    carrito = session.get("carrito", {})

    carrito = {
        str(clave): valor
        for clave, valor in carrito.items()
    }

    id = str(id)

    if id in carrito:

        carrito[id] -= 1

        if carrito[id] <= 0:
            del carrito[id]

    session["carrito"] = carrito

    return redirect(url_for("carrito"))


# =========================
# ELIMINAR PRODUCTO
# =========================

@app.route("/eliminar/<int:id>")
def eliminar(id):

    carrito = session.get("carrito", {})

    carrito = {
        str(clave): valor
        for clave, valor in carrito.items()
    }

    id = str(id)

    if id in carrito:
        del carrito[id]

    session["carrito"] = carrito

    return redirect(url_for("carrito"))


# =========================
# MOSTRAR CARRITO
# =========================

@app.route("/carrito")
def carrito():

    carrito = session.get("carrito", {})

    carrito = {
        str(clave): valor
        for clave, valor in carrito.items()
    }

    productos_carrito = []

    total = 0

    for id, cantidad in carrito.items():

        id = int(id)

        if id in productos:

            producto = productos[id].copy()

            producto["id"] = id
            producto["cantidad"] = cantidad
            producto["subtotal"] = producto["precio"] * cantidad

            productos_carrito.append(producto)

            total += producto["subtotal"]

    return render_template(
        "carrito.html",
        productos=productos_carrito,
        total=total
    )


# =========================
# VACIAR CARRITO
# =========================

@app.route("/vaciar")
def vaciar():

    session["carrito"] = {}

    return redirect(url_for("carrito"))


# =========================
# REALIZAR PEDIDO
# =========================

@app.route("/pedido", methods=["GET", "POST"])
def pedido():

    if request.method == "POST":

        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        curso = request.form["curso"]
        correo = request.form["correo"]
        telefono = request.form["telefono"]
        metodo_pago = request.form["metodo_pago"]
        carrito = session.get("carrito", {})

        total = 0

        for id, cantidad in carrito.items():

            id = int(id)

            if id in productos:
                total += productos[id]["precio"] * cantidad

        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        conexion = sqlite3.connect("pedidos.db")

        cursor = conexion.cursor()

        cursor.execute("""
        INSERT INTO pedidos
        (nombre, apellido, curso, correo, telefono, total, fecha, metodo_pago)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nombre,
            apellido,
            curso,
            correo,
            telefono,
            total,
            fecha,
            metodo_pago
        ))

        numero_pedido = cursor.lastrowid

        conexion.commit()

        conexion.close()

        session["carrito"] = {}

        return render_template(
            "confirmacion.html",
            nombre=nombre,
            total=total,
            numero_pedido=numero_pedido
        )

    return render_template("pedido.html")
# =========================
# VER PEDIDOS
# =========================

@app.route("/pedidos")
def ver_pedidos():

    conexion = sqlite3.connect("pedidos.db")
    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM pedidos
        ORDER BY id DESC
    """)

    pedidos = cursor.fetchall()

    conexion.close()

    return render_template(
        "pedidos.html",
        pedidos=pedidos
    )

# =========================
# INICIAR SERVIDOR
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)