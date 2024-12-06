from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuración de SQLite como base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gastos_comunes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos de la base de datos
class Departamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gastos = db.relationship('Gasto', backref='departamento', lazy=True)

class Gasto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    periodo = db.Column(db.String(7), nullable=False)  # Formato MM-YYYY
    monto = db.Column(db.Float, nullable=False, default=10000)
    pagado = db.Column(db.Boolean, default=False)
    fecha_pago = db.Column(db.String(10), nullable=True)  # Formato YYYY-MM-DD
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'), nullable=False)

# Inicialización de la base de datos
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

# Resto del código permanece igual...


# Endpoint para crear un departamento
@app.route('/crear_departamento', methods=['POST'])
def crear_departamento():
    data = request.json
    departamento_id = data.get("id")

    if not departamento_id:
        return jsonify({"error": "Debe especificar un ID para el departamento"}), 400

    # Verificar si el departamento ya existe
    if Departamento.query.get(departamento_id):
        return jsonify({"error": "El departamento ya existe"}), 400

    # Crear el nuevo departamento
    nuevo_departamento = Departamento(id=departamento_id)
    db.session.add(nuevo_departamento)
    db.session.commit()

    return jsonify({
        "mensaje": "Departamento creado exitosamente",
        "departamento": {"id": nuevo_departamento.id}
    }), 201

# Endpoint para generar gastos
@app.route('/generar_gastos', methods=['POST'])
def generar_gastos():
    data = request.json
    mes = data.get("mes")
    año = data.get("año")
    departamento_id = data.get("departamento_id")
    monto = data.get("monto", 10000)

    if not mes or not año:
        return jsonify({"error": "Faltan mes o año"}), 400

    if not departamento_id:
        return jsonify({"error": "Debe especificar un ID de departamento"}), 400

    departamento = Departamento.query.get(departamento_id)
    if not departamento:
        return jsonify({"error": "Departamento no encontrado"}), 404

    nuevo_gasto = Gasto(
        periodo=f"{mes:02d}-{año}",
        monto=monto,
        departamento=departamento
    )
    db.session.add(nuevo_gasto)
    db.session.commit()

    return jsonify({
        "mensaje": "Gasto común generado correctamente",
        "departamento_actualizado": departamento_id
    }), 200

# Endpoint para marcar un gasto como pagado
@app.route('/marcar_pagado', methods=['POST'])
def marcar_pagado():
    data = request.json
    departamento_id = data.get("departamento_id")
    periodo = data.get("periodo")
    fecha_pago = data.get("fecha_pago")

    if not departamento_id or not periodo or not fecha_pago:
        return jsonify({"error": "Faltan datos requeridos"}), 400

    gasto = Gasto.query.filter_by(departamento_id=departamento_id, periodo=periodo).first()
    if not gasto:
        return jsonify({"error": "Departamento o período no encontrado"}), 404

    if gasto.pagado:
        return jsonify({
            "departamento": departamento_id,
            "periodo": periodo,
            "fecha_pago": gasto.fecha_pago,
            "mensaje": "Pago duplicado"
        }), 200

    gasto.pagado = True
    gasto.fecha_pago = fecha_pago
    db.session.commit()

    plazo = datetime.strptime(periodo, "%m-%Y")
    pago = datetime.strptime(fecha_pago, "%Y-%m-%d")

    estado = "Pago exitoso dentro del plazo" if pago <= plazo.replace(day=30) else "Pago exitoso fuera de plazo"

    return jsonify({
        "departamento": departamento_id,
        "periodo": periodo,
        "fecha_pago": fecha_pago,
        "mensaje": estado
    }), 200

# Endpoint para consultar gastos pendientes
@app.route('/gastos_pendientes', methods=['GET'])
def gastos_pendientes():
    mes = request.args.get("mes", type=int)
    año = request.args.get("año", type=int)

    if not mes or not año:
        return jsonify({"error": "Faltan mes o año"}), 400

    pendientes = Gasto.query.filter(
        (Gasto.pagado == False) &
        (Gasto.periodo <= f"{mes:02d}-{año}")
    ).all()

    if not pendientes:
        return jsonify({"mensaje": "Sin montos pendientes"}), 200

    resultado = [{
        "departamento": gasto.departamento_id,
        "periodo": gasto.periodo,
        "monto": gasto.monto
    } for gasto in pendientes]

    return jsonify(resultado), 200

if __name__ == '__main__':
    app.run(debug=True)
