from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "123456"



def crear_bd():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        nombre TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre TEXT,
        descripcion TEXT,
        precio REAL,
        stock INTEGER,
        categoria TEXT
    )
    """)

    cur.execute("SELECT * FROM usuarios")

    if cur.fetchone() is None:

        cur.execute("""
        INSERT INTO usuarios
        (username,password,nombre)
        VALUES
        ('admin','123','Administrador')
        """)

    cur.execute("SELECT * FROM productos")

    if cur.fetchone() is None:

        productos = [

            ('P001','Laptop HP',
             'Core i5 16GB RAM',
             2500,10,'Tecnologia'),

            ('P002','Mouse Logitech',
             'Mouse inalámbrico',
             80,25,'Accesorios'),

            ('P003','Monitor Samsung',
             '24 pulgadas',
             850,8,'Tecnologia')

        ]

        cur.executemany("""
        INSERT INTO productos
        (codigo,nombre,descripcion,precio,stock,categoria)
        VALUES(?,?,?,?,?,?)
        """, productos)

    conn.commit()
    conn.close()

crear_bd()



@app.route("/")
def inicio():
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("""
        SELECT * FROM usuarios
        WHERE username=? AND password=?
        """,(usuario,password))

        dato = cur.fetchone()

        conn.close()

        if dato:

            session["usuario"] = usuario
            return redirect("/principal")

    return render_template("login.html")


@app.route("/principal")
def principal():

    if "usuario" not in session:
        return redirect("/login")

    return render_template(
        "principal.html",
        usuario=session["usuario"]
    )


@app.route("/buscador")
def buscador():

    if "usuario" not in session:
        return redirect("/login")

    return render_template("buscador.html")


@app.route("/api/buscar_producto",
methods=["POST"])
def buscar_producto():

    codigo = request.json["codigo"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT codigo,nombre,descripcion,
           precio,stock,categoria
    FROM productos
    WHERE codigo=?
    """,(codigo,))

    producto = cur.fetchone()

    conn.close()

    if producto:

        return jsonify({

            "codigo":producto[0],
            "nombre":producto[1],
            "descripcion":producto[2],
            "precio":producto[3],
            "stock":producto[4],
            "categoria":producto[5]

        })

    return jsonify({
        "mensaje":"Producto no encontrado"
    })



@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)