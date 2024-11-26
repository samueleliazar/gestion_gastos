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
    try:
        mes = int(data.get("mes"))  
        año = int(data.get("año")) 
    except (ValueError, TypeError):
        return jsonify({"error": "Mes y año deben ser números válidos"}), 400

    departamento_ids = data.get("departamento_ids")
    monto = data.get("monto", 10000)

    if not departamento_ids or not isinstance(departamento_ids, list):
        return jsonify({"error": "Debe especificar una lista de departamentos"}), 400

    departamentos_actualizados = []
    for depto in departamentos:
        if depto["id"] in departamento_ids:
            depto["gastos"].append({
                "periodo": f"{mes:02d}-{año}",
                "monto": monto,
                "pagado": False,
                "fecha_pago": None
            })
            departamentos_actualizados.append(depto["id"])

    if not departamentos_actualizados:
        return jsonify({"mensaje": "No se encontraron departamentos válidos"}), 404

    return jsonify({
        "mensaje": "Gastos comunes generados correctamente",
        "departamentos_actualizados": departamentos_actualizados
    }), 200
    
    

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
