let precioPergaminoKg = 0;
let precioPasillaKg = 0;
let ultimaActualizacionPrecios = null;

document.addEventListener('DOMContentLoaded', function() {
    // Obtener referencias a elementos del DOM específicos del dashboard y el modal
    const openModalBtn = document.querySelector('button.bg-green-600'); // Botón 'Registrar Venta' en el dashboard
    const modal = document.getElementById('registroVentaModal');
    const closeModalBtn = document.getElementById('cerrarModalBtn');
    const formRegistroVenta = document.getElementById('formRegistroVenta');
    const registrarVentaBtnModal = document.getElementById('registrarVentaBtnModal');
    const tipoCafeSelect = document.getElementById('tipo_cafe');
    const precioKgInput = document.getElementById('precio_kg');
    const cantidadInput = document.getElementById('cantidad'); // Obtener el input de cantidad
    const totalVentaElement = document.getElementById('total_venta'); // Obtener el elemento para mostrar el total

    // Función para obtener y calcular los precios por Kg y actualizar el dashboard
    function fetchAndCalculatePrices() {
        fetch('http://127.0.0.1:5000/api/precios_cafe')
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => { throw new Error(`HTTP error! status: ${response.status}, body: ${text}`); });
                }
                return response.json();
            })
            .then(data => {
                console.log('Datos de precios recibidos del backend (Dashboard): ', data);

                // Limpiar y convertir precios a números
                const precioPergaminoCargaStr = data.precio_pergamino || '0';
                const precioPasillaArrobaStr = data.precio_pasilla || '0';

                const cleanPrecioPergamino = precioPergaminoCargaStr.replace(/[^0-9]/g, '');
                const cleanPrecioPasilla = precioPasillaArrobaStr.replace(/[^0-9]/g, '');

                const precioPergaminoCarga = parseFloat(cleanPrecioPergamino);
                const precioPasillaArroba = parseFloat(cleanPrecioPasilla);

                console.log('Precios limpiados y parseados (Dashboard): ', { precioPergaminoCarga, precioPasillaArroba });

                // Calcular precio por Kg (1 carga = 125kg, 1 arroba = 12.5kg)
                if (!isNaN(precioPergaminoCarga) && precioPergaminoCarga > 0) {
                    precioPergaminoKg = precioPergaminoCarga / 125;
                }
                if (!isNaN(precioPasillaArroba) && precioPasillaArroba > 0) {
                    precioPasillaKg = precioPasillaArroba / 12.5;
                }

                ultimaActualizacionPrecios = data.fecha_actualizacion || new Date().toISOString();
                console.log('Precios calculados por Kg (Dashboard):', { precioPergaminoKg, precioPasillaKg, ultimaActualizacionPrecios });

                // Actualizar los elementos en el HTML del dashboard con los precios obtenidos
                const precioArabicoCargaElement = document.getElementById('precio-arabico-carga');
                const precioPasillaArrobaElement = document.getElementById('precio-pasilla-arroba');
                const fechaPreciosMercadoElement = document.getElementById('fecha-precios-mercado');
                const precioArabicoKgElement = document.getElementById('precio-arabico-kg'); // Nuevo elemento en el dashboard
                const precioPasillaKgElement = document.getElementById('precio-pasilla-kg'); // Nuevo elemento en el dashboard

                if (precioArabicoCargaElement && data.precio_pergamino !== undefined) {
                    const precioCarga = parseFloat(data.precio_pergamino.replace(/[^0-9]/g, ''));
                    if (!isNaN(precioCarga)) {
                        precioArabicoCargaElement.innerText = `$${precioCarga.toLocaleString('es-CO')}`;
                    } else {
                        precioArabicoCargaElement.innerText = 'N/A';
                    }
                }

                if (precioPasillaArrobaElement && data.precio_pasilla !== undefined) {
                    const precioPasilla = parseFloat(data.precio_pasilla.replace(/[^0-9]/g, ''));
                    if (!isNaN(precioPasilla)) {
                        precioPasillaArrobaElement.innerText = `$${precioPasilla.toLocaleString('es-CO')}`;
                    } else {
                        precioPasillaArrobaElement.innerText = 'N/A';
                    }
                }

                 if (precioArabicoKgElement && !isNaN(precioPergaminoKg)) {
                    precioArabicoKgElement.innerText = `$${precioPergaminoKg.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} COP`;
                 } else if (precioArabicoKgElement) {
                     precioArabicoKgElement.innerText = 'N/A';
                 }

                 if (precioPasillaKgElement && !isNaN(precioPasillaKg)) {
                    precioPasillaKgElement.innerText = `$${precioPasillaKg.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} COP`;
                 } else if (precioPasillaKgElement) {
                      precioPasillaKgElement.innerText = 'N/A';
                 }

                // Actualizar fecha
                if (fechaPreciosMercadoElement && data.fecha_actualizacion) {
                    try {
                        const fecha = new Date(data.fecha_actualizacion);
                        fechaPreciosMercadoElement.innerText = `Precios actualizados al ${fecha.toLocaleDateString('es-CO')}`; // Usar es-CO para formato local
                    } catch (e) {
                        console.error('Error parsing date:', e);
                        fechaPreciosMercadoElement.innerText = 'Fecha no disponible';
                    }
                } else if (fechaPreciosMercadoElement) {
                     fechaPreciosMercadoElement.innerText = 'Fecha no disponible';
                }

                // Si el modal ya está abierto y hay un tipo de café seleccionado, actualizar el precio
                 if (!modal.classList.contains('hidden')) { // Verificar si el modal está visible
                    const selectedType = tipoCafeSelect.value;
                     if (selectedType) {
                         if (selectedType === 'Pasilla') {
                             precioKgInput.value = precioPasillaKg.toFixed(2);
                         } else if (selectedType === 'Arabica') {
                             precioKgInput.value = precioPergaminoKg.toFixed(2);
                         }
                         updateTotal(); // Recalcular el total con el nuevo precio
                     }
                 }
            })
            .catch(error => {
                console.error('Error fetching or calculating coffee prices (Dashboard):', error);
                // Mostrar un mensaje de error en los campos de precio si falla
                const precioKgInputModal = document.getElementById('precio_kg');
                if (precioKgInputModal) precioKgInputModal.value = 'Error';
                updateTotal(); // Resetear el total mostrado en el modal

                // Mostrar mensaje de error en los elementos de precio en la página del dashboard
                const precioArabicoCargaElement = document.getElementById('precio-arabico-carga');
                const precioPasillaArrobaElement = document.getElementById('precio-pasilla-arroba');
                const fechaPreciosMercadoElement = document.getElementById('fecha-precios-mercado');
                const precioArabicoKgElement = document.getElementById('precio-arabico-kg');
                const precioPasillaKgElement = document.getElementById('precio-pasilla-kg');

                if (precioArabicoCargaElement) precioArabicoCargaElement.innerText = 'Error';
                if (precioPasillaArrobaElement) precioPasillaArrobaElement.innerText = 'Error';
                if (fechaPreciosMercadoElement) fechaPreciosMercadoElement.innerText = 'Error al cargar precios';
                 if (precioArabicoKgElement) precioArabicoKgElement.innerText = 'Error';
                 if (precioPasillaKgElement) precioPasillaKgElement.innerText = 'Error';
            });
    }

    // Función para obtener y mostrar el historial de ventas del campesino en el dashboard
    function fetchRecentVentasCampesino() {
        const jwtToken = localStorage.getItem('access_token');

        console.log('JWT Token fetched for recent ventas (Dashboard):', jwtToken);

        if (!jwtToken) {
            console.error('No JWT token found for recent sales (Dashboard). User not authenticated?');
            // Podrías redirigir o mostrar un mensaje, dependiendo del flujo deseado si no hay token al cargar el dashboard
            return;
        }

        fetch('http://127.0.0.1:5000/api/campesino/dashboard', { // Asumiendo que esta ruta devuelve stats y ventas_recientes
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + jwtToken
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Error al obtener datos del dashboard'); });
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos del dashboard recibidos:', data);

            // Actualizar las estadísticas (aunque hay otra función, la llamamos aquí para consistencia con la carga)
            if (data.stats) {
                calculateAndDisplayStats(data.stats);
            }

            // Poblar la tabla de ventas recientes
            if (data.ventas_recientes) {
                populateRecentSalesTable(data.ventas_recientes);
            } else {
                 // Limpiar tabla si no hay ventas recientes o hay un error en los datos
                 const tbody = document.querySelector('#recent-sales-table tbody');
                 if (tbody) {
                      tbody.innerHTML = `<tr><td colspan="7" class="px-6 py-4 text-center text-gray-500">No hay ventas recientes disponibles.</td></tr>`;
                 }
            }
        })
        .catch(error => {
            console.error('Error fetching dashboard data:', error);
            // Mostrar mensaje de error en la tabla y estadísticas si falla
            const tbody = document.querySelector('#recent-sales-table tbody');
             if (tbody) {
                 tbody.innerHTML = `<tr><td colspan="7" class="px-6 py-4 text-center text-red-500">Error al cargar ventas recientes: ${error.message}</td></tr>`;
             }
             // Opcional: Mostrar error en las tarjetas de estadísticas también
             const totalVentasValueElement = document.getElementById('total-ventas-value');
             // ... similar para otras estadísticas
             if (totalVentasValueElement) totalVentasValueElement.innerText = 'Error';
        });
    }

    // Función para poblar la tabla de ventas recientes en el dashboard
    function populateRecentSalesTable(ventas) {
        const tbody = document.querySelector('#recent-sales-table tbody');
        if (!tbody) {
            console.error('Table body not found for dashboard update!');
            return;
        }

        tbody.innerHTML = ''; // Limpiar contenido actual de la tabla

        if (!ventas || ventas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="px-6 py-4 text-center text-gray-500">No hay ventas recientes disponibles.</td></tr>`;
            return;
        }

        ventas.forEach(venta => {
            // Formatear la fecha a DD/MM/YYYY. Asegurarse de que venta.fecha sea válido.
            const fechaVenta = venta.fecha ? new Date(venta.fecha).toLocaleDateString('es-CO') : 'N/A';

            // Obtener tipo de café. El backend ya debería enviarlo como string.
            const tipoCafe = venta.tipo_cafe || 'N/A';

            // Obtener cantidad. Asegurarse de que venta.cantidad sea un número.
            const cantidad = venta.cantidad !== null && venta.cantidad !== undefined ? parseFloat(venta.cantidad) : 0;
            const cantidadFormateada = cantidad.toLocaleString('es-CO', { maximumFractionDigits: 2 }); // Formatear cantidad

            // Obtener y formatear total. Asegurarse de que venta.total sea un número.
            const total = venta.total !== null && venta.total !== undefined ? parseFloat(venta.total) : 0;
            const totalFormateado = `$${total.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} COP`;

            // Obtener estado
            const estado = venta.estado || 'Pendiente';

            // Determinar la clase CSS según el estado
            let estadoClass = '';
            switch(estado) {
                case 'Completada':
                    estadoClass = 'bg-green-100 text-green-800';
                    break;
                case 'Pendiente':
                    estadoClass = 'bg-yellow-100 text-yellow-800';
                    break;
                default:
                    estadoClass = 'bg-gray-100 text-gray-800'; // Color por defecto para otros estados
            }

            // Determinar la clase CSS según el tipo de café
            let tipoCafeClass = '';
            switch(tipoCafe) {
                case 'Pasilla':
                    tipoCafeClass = 'bg-yellow-100 text-yellow-800';
                    break;
                case 'Arabica':
                    tipoCafeClass = 'bg-green-100 text-green-800';
                    break;
                default:
                    tipoCafeClass = 'bg-gray-100 text-gray-800'; // Color por defecto
            }

            const row = `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${fechaVenta}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${venta.comprador || 'CafExport'}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span class="px-2 py-1 ${tipoCafeClass} rounded-full text-sm">
                            ${tipoCafe}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        ${cantidadFormateada} kg
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        ${totalFormateado}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span class="px-2 py-1 ${estadoClass} rounded-full text-sm">
                            ${estado}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">
                        <button class="text-gray-400 hover:text-gray-600"><i class="fas fa-ellipsis-v"></i></button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    }

     // ** Función para actualizar las estadísticas de ventas en el dashboard **
     function calculateAndDisplayStats(stats) {
         // Elemento para mostrar el total de INGRESOS en el dashboard
         const dashboardTotalIngresosElement = document.getElementById('dashboard-total-ingresos-value');

         // Otros elementos de estadísticas que quizás necesiten actualizarse desde stats
         const totalVentasValueElement = document.getElementById('total-ventas-value'); // Este podría ser un ID diferente si hay un contador de ventas
         const completadasValueElement = document.getElementById('completadas-value');
         const pendientesValueElement = document.getElementById('pendientes-value');
         // const totalIngresosValueElement = document.getElementById('total-ingresos-value'); // Este ID ya no se usa para ingresos en el dashboard
         const promedioValueElement = document.getElementById('promedio-value');


         if (dashboardTotalIngresosElement && stats.total_ingresos !== undefined) {
             // Mostrar el total de ingresos formateado como moneda COP
             dashboardTotalIngresosElement.innerText = `$${parseFloat(stats.total_ingresos).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} COP`;
         } else if (dashboardTotalIngresosElement) {
              dashboardTotalIngresosElement.innerText = '$ 0 COP'; // O algún valor predeterminado si no hay datos
         }

         // Actualizar el conteo total de ventas si existe un elemento para ello (ej. en la sección de ventas recientes)
         // Aunque la tarjeta principal ahora es de ingresos, podría haber un lugar donde se muestre el *número* total de ventas
         // Si el ID '#total-ventas-value' se mantiene para el CONTEO en el dashboard (aunque el nombre de la tarjeta era confuso)
         // entonces lo actualizamos aquí con stats.total_ventas
         if (totalVentasValueElement && stats.total_ventas !== undefined) {
             totalVentasValueElement.innerText = stats.total_ventas; // Mostrar el número total de ventas
         } else if (totalVentasValueElement) {
             totalVentasValueElement.innerText = '0';
         }


         if (completadasValueElement && stats.completadas !== undefined) {
             completadasValueElement.innerText = stats.completadas;
         } else if (completadasValueElement) {
              completadasValueElement.innerText = '0';
         }

         if (pendientesValueElement && stats.pendientes !== undefined) {
             pendientesValueElement.innerText = stats.pendientes;
         } else if (pendientesValueElement) {
             pendientesValueElement.innerText = '0';
         }

         // El promedio ahora se actualiza con el nuevo cálculo del backend
         if (promedioValueElement && stats.promedio !== undefined) {
             promedioValueElement.innerText = `$${parseFloat(stats.promedio).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} COP`;
         } else if (promedioValueElement) {
             promedioValueElement.innerText = '$ 0 COP';
         }
     }

    // Mostrar modal
    if (openModalBtn) { // Asegurarse de que el botón existe en esta página
        openModalBtn.addEventListener('click', function() {
            modal.classList.remove('hidden');
            // Al abrir el modal, asegurar que los precios estén cargados
            fetchAndCalculatePrices();
        });
    }

    // Ocultar modal al hacer clic en la 'x' o fuera del modal
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', function() {
            modal.classList.add('hidden');
            formRegistroVenta.reset(); // Resetear formulario al cerrar
            updateTotal(); // Resetear el total mostrado
        });
    }

    if (modal) { // Asegurarse de que el modal existe en esta página
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.classList.add('hidden');
                formRegistroVenta.reset(); // Resetear formulario al cerrar
                updateTotal(); // Resetear el total mostrado
            }
        });
    }

    // Rellenar precio por Kg al seleccionar tipo de café en el modal
    if (tipoCafeSelect) {
        tipoCafeSelect.addEventListener('change', function() {
            const selectedType = tipoCafeSelect.value;
            console.log('Tipo de café seleccionado (Modal):', selectedType);
            if (selectedType === 'Pasilla') {
                precioKgInput.value = precioPasillaKg.toFixed(2);
            } else if (selectedType === 'Arabica') {
                precioKgInput.value = precioPergaminoKg.toFixed(2);
            } else {
                precioKgInput.value = '';
            }
            updateTotal(); // Actualizar el total al cambiar el tipo de café
        });
    }

    // Actualizar total al cambiar cantidad o precio en el modal
    if (cantidadInput) { // Asegurarse de que el input existe
        cantidadInput.addEventListener('input', updateTotal);
    }
    if (precioKgInput) { // Asegurarse de que el input existe
         precioKgInput.addEventListener('input', updateTotal);
    }

    // Función para calcular y mostrar el total en el modal
    function updateTotal() {
        const cantidad = parseFloat(cantidadInput.value) || 0;
        const precioKg = parseFloat(precioKgInput.value) || 0;
        const total = cantidad * precioKg;
        // Formatear el total con separadores de miles y dos decimales
        totalVentaElement.innerText = total.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    // Lógica para enviar el formulario de registro de venta desde el modal
    if (registrarVentaBtnModal) {
        registrarVentaBtnModal.addEventListener('click', function() {
            if (formRegistroVenta.checkValidity()) {
                const formData = new FormData(formRegistroVenta);

                let cantidad = parseFloat(document.getElementById('cantidad').value);
                let tipo_cafe = formData.get('tipo_cafe');
                let precio_kg = parseFloat(document.getElementById('precio_kg').value);

                const dataToSend = {
                    cantidad: cantidad,
                    tipo_cafe: tipo_cafe,
                    precio_kg: precio_kg
                };

                const jwtToken = localStorage.getItem('access_token');

                fetch('http://127.0.0.1:5000/api/ventas', { // Endpoint para registrar ventas
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + jwtToken
                    },
                    body: JSON.stringify(dataToSend)
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw new Error(err.error || 'Error al registrar la venta'); });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Venta registrada con éxito:', data);
                    alert(data.mensaje || 'Venta registrada con éxito');
                    modal.classList.add('hidden');
                    formRegistroVenta.reset();
                    updateTotal();

                    // Recargar los datos del dashboard después de registrar una venta
                    fetchRecentVentasCampesino(); // Actualizar tabla de ventas recientes y estadísticas
                    fetchAndCalculatePrices(); // Asegurar que los precios mostrados también se actualicen si es necesario

                })
                .catch((error) => {
                    console.error('Error al registrar la venta:', error);
                    alert('Error al registrar la venta: ' + error.message);
                });

            } else {
                formRegistroVenta.reportValidity();
            }
        });
    }

    // Cargar datos al cargar la página del dashboard
    fetchAndCalculatePrices(); // Cargar precios del mercado
    fetchRecentVentasCampesino(); // Cargar ventas recientes y estadísticas

}); 