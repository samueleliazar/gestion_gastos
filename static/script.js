
document.getElementById('generar-gastos-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const mes = document.getElementById('mes').value;
    const año = document.getElementById('año').value;
    const departamentoId = parseInt(document.getElementById('departamento-id-generar').value); 
    const monto = document.getElementById('monto').value;

    try {
        const response = await fetch('/generar_gastos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mes: parseInt(mes),
                año: parseInt(año),
                departamento_id: departamentoId,
                monto: parseInt(monto)
            })
        });

        const result = await response.json();
        mostrarResultadoGastos(result, response.ok);
    } catch (error) {
        console.error("Error al generar gastos:", error);
    }
});

function mostrarResultadoGastos(data, ok) {
    const resultado = document.getElementById('resultado-gastos');
    resultado.className = `alert ${ok ? 'alert-success' : 'alert-danger'} d-block`;
    resultado.textContent = data.mensaje || JSON.stringify(data);
}

document.getElementById('consultar-gastos-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const mes = document.getElementById('mes-consulta').value;
    const año = document.getElementById('año-consulta').value;

    try {
        const response = await fetch(`/gastos_pendientes?mes=${mes}&año=${año}`);
        const result = await response.json();
        mostrarPendientes(result, response.ok);
    } catch (error) {
        console.error("Error al consultar gastos:", error);
    }
});

function mostrarPendientes(data, ok) {
    const pendientes = document.getElementById('pendientes');
    pendientes.innerHTML = '';

    if (ok && Array.isArray(data)) {
        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'alert alert-info';
            div.textContent = `Departamento: ${item.departamento}, Periodo: ${item.periodo}, Monto: ${item.monto}`;
            pendientes.appendChild(div);
        });
    } else {
        const div = document.createElement('div');
        div.className = `alert ${ok ? 'alert-success' : 'alert-danger'}`;
        div.textContent = data.mensaje || JSON.stringify(data);
        pendientes.appendChild(div);
    }
}


document.getElementById('marcar-pagado-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const departamentoId = document.getElementById('departamento-id-pagado').value;
    const periodo = document.getElementById('periodo').value;
    const fechaPago = document.getElementById('fecha-pago').value;

    try {
        const response = await fetch('/marcar_pagado', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                departamento_id: parseInt(departamentoId),
                periodo,
                fecha_pago: fechaPago
            })
        });

        const result = await response.json();
        mostrarResultadoPago(result, response.ok);
    } catch (error) {
        console.error("Error al marcar como pagado:", error);
    }
});

function mostrarResultadoPago(data, ok) {
    const resultado = document.getElementById('resultado-pago');
    resultado.className = `alert ${ok ? 'alert-success' : 'alert-danger'} d-block`;
    resultado.textContent = data.mensaje || JSON.stringify(data);
}

document.getElementById('crear-departamento-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const departamentoId = parseInt(document.getElementById('departamento-id-crear').value);

    try {
        const response = await fetch('/crear_departamento', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: departamentoId })
        });

        const result = await response.json();
        mostrarResultadoCrearDepartamento(result, response.ok);
    } catch (error) {
        console.error("Error al crear departamento:", error);
    }
});

function mostrarResultadoCrearDepartamento(data, ok) {
    const resultado = document.getElementById('resultado-crear-departamento');
    resultado.className = `alert ${ok ? 'alert-success' : 'alert-danger'} d-block`;
    resultado.textContent = data.mensaje || JSON.stringify(data);
}
