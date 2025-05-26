let precioPergaminoKg = 0;
let precioPasillaKg = 0;
let ultimaActualizacionPrecios = null;

document.addEventListener('DOMContentLoaded', function() {
    const openModalBtn = document.querySelector('button.bg-green-600'); // Botón 'Registrar Venta'
    const modal = document.getElementById('registroVentaModal');
    const closeModalBtn = document.getElementById('cerrarModalBtn');
    const formRegistroVenta = document.getElementById('formRegistroVenta');
    const registrarVentaBtnModal = document.getElementById('registrarVentaBtnModal');
    const tipoCafeSelect = document.getElementById('tipo_cafe');
    const precioKgInput = document.getElementById('precio_kg');
    const cantidadInput = document.getElementById('cantidad'); // Obtener el input de cantidad
    const totalVentaElement = document.getElementById('total_venta'); // Obtener el elemento para mostrar el total

    // Función para obtener y calcular los precios por Kg
    function fetchAndCalculatePrices() {
        fetch('http://127.0.0.1:5000/api/precios_cafe')
            .then(response => {
                if (!response.ok) {
                    // Intentar leer el cuerpo del error si está disponible
                    return response.text().then(text => { throw new Error(`HTTP error! status: ${response.status}, body: ${text}`); });
                }
                return response.json();
            })
            .then(data => {
                console.log('Datos de precios recibidos del backend:', data);

                // Limpiar y convertir precios a números
                // Usar replace para eliminar puntos de miles y comas, si existen
                const precioPergaminoCargaStr = data.precio_pergamino || '0';
                const precioPasillaArrobaStr = data.precio_pasilla || '0';

                // Eliminar todo lo que no sea dígito o punto, luego asegurar que solo haya un punto decimal si es necesario
                const cleanPrecioPergamino = precioPergaminoCargaStr.replace(/[^0-9.,]/g, '').replace(',', '.'); // Reemplazar coma por punto decimal si existe
                const cleanPrecioPasilla = precioPasillaArrobaStr.replace(/[^0-9.,]/g, '').replace(',', '.');

                const precioPergaminoCarga = parseFloat(cleanPrecioPergamino);
                const precioPasillaArroba = parseFloat(cleanPrecioPasilla);

                console.log('Precios limpiados y parseados:', { precioPergaminoCarga, precioPasillaArroba });

                // Calcular precio por Kg (1 carga = 125kg, 1 arroba = 12.5kg)
                if (!isNaN(precioPergaminoCarga) && precioPergaminoCarga > 0) {
                    // Asumimos que el precio de referencia es por carga de 125kg
                    precioPergaminoKg = precioPergaminoCarga / 125; // Precio por carga (125kg)
                }
                if (!isNaN(precioPasillaArroba) && precioPasillaArroba > 0) {
                     // Asumimos que el precio de pasilla es por arroba de 12.5kg
                    precioPasillaKg = precioPasillaArroba / 12.5; // Precio por arroba (12.5kg)
                }

                ultimaActualizacionPrecios = data.fecha_actualizacion || new Date().toISOString();
                console.log('Precios calculados por Kg:', { precioPergaminoKg, precioPasillaKg, ultimaActualizacionPrecios });

                // Opcional: Si el modal ya está abierto y hay un tipo de café seleccionado, actualizar el precio
                 const selectedTypeOnLoad = tipoCafeSelect.value;
                 if (selectedTypeOnLoad) {
                     if (selectedTypeOnLoad === 'Pasilla') {
                         precioKgInput.value = precioPasillaKg.toFixed(2);
                     } else if (selectedTypeOnLoad === 'Arabica') { // Asegurarse de usar 'Arabica' si ese es el valor del Enum
                         precioKgInput.value = precioPergaminoKg.toFixed(2);
                     }
                     updateTotal(); // Recalcular el total con el nuevo precio
                 }

            })
            .catch(error => {
                console.error('Error fetching or calculating coffee prices:', error);
                // Mostrar un mensaje de error en el campo de precio si falla
                 precioKgInput.value = 'Error';
                 updateTotal(); // Resetear el total si no se pudo obtener el precio
            });
    }

    // Llamar a la función al cargar la página
    fetchAndCalculatePrices();

    // Mostrar modal
    openModalBtn.addEventListener('click', function() {
        modal.classList.remove('hidden');
    });

    // Ocultar modal al hacer clic en la 'x' o fuera del modal
    closeModalBtn.addEventListener('click', function() {
        modal.classList.add('hidden');
        formRegistroVenta.reset(); // Resetear formulario al cerrar
        updateTotal(); // Resetear el total mostrado
    });

    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.classList.add('hidden');
            formRegistroVenta.reset(); // Resetear formulario al cerrar
            updateTotal(); // Resetear el total mostrado
        }
    });

    // Rellenar precio por Kg al seleccionar tipo de café
    tipoCafeSelect.addEventListener('change', function() {
        const selectedType = tipoCafeSelect.value;
        console.log('Tipo de café seleccionado:', selectedType);
        if (selectedType === 'Pasilla') {
            precioKgInput.value = precioPasillaKg.toFixed(2);
        } else if (selectedType === 'Arabica') { // Asegurarse de usar 'Arabica'
            precioKgInput.value = precioPergaminoKg.toFixed(2);
        } else {
            precioKgInput.value = '';
        }
        updateTotal(); // Actualizar el total al cambiar el tipo de café
    });

    // Actualizar total al cambiar cantidad o precio
    cantidadInput.addEventListener('input', updateTotal); // Escuchar cambios en cantidad
    precioKgInput.addEventListener('input', updateTotal); // Escuchar cambios en precio

    // Función para calcular y mostrar el total
    function updateTotal() {
        const cantidad = parseFloat(cantidadInput.value) || 0;
        const precioKg = parseFloat(precioKgInput.value) || 0;
        const total = cantidad * precioKg;
        totalVentaElement.innerText = total.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    // Lógica para enviar el formulario
    registrarVentaBtnModal.addEventListener('click', function() {
        if (formRegistroVenta.checkValidity()) {
            const formData = new FormData(formRegistroVenta);
            const data = Object.fromEntries(formData.entries());

            const jwtToken = localStorage.getItem('access_token');

            fetch('http://127.0.0.1:5000/api/ventas', { // Asegurarse de usar el puerto 5000
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + jwtToken
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || 'Error al registrar la venta'); });
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', data);
                alert(data.mensaje || 'Venta registrada con éxito');
                modal.classList.add('hidden');
                formRegistroVenta.reset(); // Resetear formulario
                updateTotal(); // Resetear el total mostrado
                // Opcional: Recargar la página o actualizar la tabla de ventas
                // window.location.reload();
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Error al registrar la venta: ' + error.message);
            });

        } else {
            formRegistroVenta.reportValidity();
        }
    });
}); 