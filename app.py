from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)


departamentos = [
    {"id": 101, "gastos": []},
    {"id": 102, "gastos": []},
    {"id": 1305, "gastos": []}
]

@app.route('/')
def home():
    return render_template('index.html')

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


    for depto in departamentos:
        if depto["id"] == departamento_id:
            depto["gastos"].append({
                "periodo": f"{mes:02d}-{año}",
                "monto": monto,
                "pagado": False,
                "fecha_pago": None
            })
            return jsonify({
                "mensaje": "Gasto común generado correctamente",
                "departamento_actualizado": departamento_id
            }), 200

    return jsonify({"error": "Departamento no encontrado"}), 404
    
    

@app.route('/marcar_pagado', methods=['POST'])
def marcar_pagado():
    data = request.json
    departamento_id = data.get("departamento_id")
    periodo = data.get("periodo")
    fecha_pago = data.get("fecha_pago")

    if not departamento_id or not periodo or not fecha_pago:
        return jsonify({"error": "Faltan datos requeridos"}), 400

    for depto in departamentos:
        if depto["id"] == departamento_id:
            for gasto in depto["gastos"]:
                if gasto["periodo"] == periodo:
                    if gasto["pagado"]:
                        return jsonify({
                            "departamento": departamento_id,
                            "periodo": periodo,
                            "fecha_pago": gasto["fecha_pago"],
                            "mensaje": "Pago duplicado"
                        }), 200

                    gasto["pagado"] = True
                    gasto["fecha_pago"] = fecha_pago

                    plazo = datetime.strptime(periodo, "%m-%Y")
                    pago = datetime.strptime(fecha_pago, "%Y-%m-%d")

                    if pago <= plazo.replace(day=30):  
                        estado = "Pago exitoso dentro del plazo"
                    else:
                        estado = "Pago exitoso fuera de plazo"

                    return jsonify({
                        "departamento": departamento_id,
                        "periodo": periodo,
                        "fecha_pago": fecha_pago,
                        "mensaje": estado
                    }), 200

    return jsonify({"error": "Departamento o período no encontrado"}), 404


@app.route('/gastos_pendientes', methods=['GET'])
def gastos_pendientes():
    mes = request.args.get("mes", type=int)
    año = request.args.get("año", type=int)

    if not mes or not año:
        return jsonify({"error": "Faltan mes o año"}), 400

    pendientes = []
    for depto in departamentos:
        for gasto in depto["gastos"]:
            gasto_mes, gasto_año = map(int, gasto["periodo"].split("-"))
            if gasto_año < año or (gasto_año == año and gasto_mes <= mes):
                if not gasto["pagado"]:
                    pendientes.append({
                        "departamento": depto["id"],
                        "periodo": gasto["periodo"],
                        "monto": gasto["monto"]
                    })

    if not pendientes:
        return jsonify({"mensaje": "Sin montos pendientes"}), 200

    pendientes.sort(key=lambda x: datetime.strptime(x["periodo"], "%m-%Y"))
    return jsonify(pendientes), 200

if __name__ == '__main__':
    app.run(debug=True)
