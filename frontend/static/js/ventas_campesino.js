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
                const cleanPrecioPergamino = precioPergaminoCargaStr.replace(/[^0-9]/g, '');
                const cleanPrecioPasilla = precioPasillaArrobaStr.replace(/[^0-9]/g, '');

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

                // Actualizar los nuevos elementos en el HTML de ventas_campesino.html con los precios obtenidos
                const precioArabicoCargaElement = document.getElementById('precio-arabico-carga');
                const precioPasillaArrobaElement = document.getElementById('precio-pasilla-arroba');
                const fechaPreciosMercadoElement = document.getElementById('fecha-precios-mercado');

                if (precioArabicoCargaElement && data.precio_pergamino !== undefined) {
                     // Eliminar caracteres no numéricos y formatear
                    const precioCarga = parseFloat(data.precio_pergamino.replace(/[^0-9]/g, ''));
                    if (!isNaN(precioCarga)) {
                        precioArabicoCargaElement.innerText = `$${precioCarga.toLocaleString('es-CO')}`;
                    } else {
                        precioArabicoCargaElement.innerText = 'N/A';
                    }
                }

                if (precioPasillaArrobaElement && data.precio_pasilla !== undefined) {
                     // Eliminar caracteres no numéricos y formatear
                    const precioPasilla = parseFloat(data.precio_pasilla.replace(/[^0-9]/g, ''));
                     if (!isNaN(precioPasilla)) {
                         precioPasillaArrobaElement.innerText = `$${precioPasilla.toLocaleString('es-CO')}`;
                     } else {
                         precioPasillaArrobaElement.innerText = 'N/A';
                     }
                }

                // Actualizar fecha
                if (fechaPreciosMercadoElement && data.fecha_actualizacion) {
                     try {
                        const fecha = new Date(data.fecha_actualizacion);
                        fechaPreciosMercadoElement.innerText = `Precios actualizados al ${fecha.toLocaleDateString()}`;
                     } catch (e) {
                         console.error('Error parsing date:', e);
                         fechaPreciosMercadoElement.innerText = 'Fecha no disponible';
                     }
                }

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

                // Suponiendo que 'data' es la respuesta JSON exitosa del backend
                if (data.token) {
                    localStorage.setItem('access_token', data.token);
                    // Ahora redirige al usuario a la página correspondiente (dashboard, ventas, etc.)
                } else {
                    // Manejar caso donde no se recibe token (debería haber un error del backend)
                }

            })
            .catch(error => {
                console.error('Error fetching or calculating coffee prices:', error);
                // Mostrar un mensaje de error en el campo de precio si falla
                 precioKgInput.value = 'Error';
                 updateTotal(); // Resetear el total si no se pudo obtener el precio
                // Opcional: Mostrar mensaje de error en los nuevos elementos de precio en la página
                const precioArabicoCargaElement = document.getElementById('precio-arabico-carga');
                const precioPasillaArrobaElement = document.getElementById('precio-pasilla-arroba');
                const fechaPreciosMercadoElement = document.getElementById('fecha-precios-mercado');
                if (precioArabicoCargaElement) precioArabicoCargaElement.innerText = 'Error';
                if (precioPasillaArrobaElement) precioPasillaArrobaElement.innerText = 'Error';
                if (fechaPreciosMercadoElement) fechaPreciosMercadoElement.innerText = 'Error al cargar precios';
            });
    }

    // Llamar a la función al cargar la página
    fetchAndCalculatePrices();

    // Función para obtener y mostrar el historial de ventas del campesino
    function fetchVentasCampesino() {
        const jwtToken = localStorage.getItem('access_token'); // Obtener el token JWT

        console.log('JWT Token fetched for ventas:', jwtToken); // Línea de depuración

        if (!jwtToken) {
            console.error('No JWT token found. User not authenticated?');
            // NOTA IMPORTANTE: Si ves este error al cargar la página después de iniciar sesión,
            // el problema está en el script JavaScript que maneja el inicio de sesión.
            // Debes asegurar que tras un login exitoso a /api/auth/login,
            // el token JWT recibido del backend se guarde en localStorage con la clave 'access_token'.
            // Ejemplo: localStorage.setItem('access_token', data.token);
            // Redirigir a la página de login del campesino si no hay token
            alert('Tu sesión ha expirado o no has iniciado sesión. Por favor, inicia sesión de nuevo.');
            window.location.href = '/campesino/login'; // Ajusta esta URL si es diferente
            return;
        }

        fetch('http://127.0.0.1:5000/api/ventas', { // Usar la ruta de ventas del blueprint ventas_bp
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + jwtToken // Incluir el token JWT
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Error al obtener historial de ventas'); });
            }
            return response.json();
        })
        .then(ventas => {
            console.log('Historial de ventas recibido:', ventas);
            
            // Calcular y actualizar las estadísticas basadas en los datos de ventas recibidos
            calculateAndDisplayStats(ventas);

            populateVentasTable(ventas); // Llenar la tabla con los datos
        })
        .catch(error => {
            console.error('Error fetching sales history:', error);
            // Mostrar mensaje de error en la tabla o en la consola
            const tbody = document.querySelector('#ventasTable tbody');
            if (tbody) {
                tbody.innerHTML = `<tr><td colspan="7" class="px-6 py-4 text-center text-red-500">Error al cargar ventas: ${error.message}</td></tr>`;
            }
        });
    }

    // Función para poblar la tabla de ventas con los datos recibidos
    function populateVentasTable(ventas) {
        const tbody = document.querySelector('#ventasTable tbody');
        if (!tbody) {
            console.error('Table body not found!');
            return;
        }

        tbody.innerHTML = ''; // Limpiar contenido actual de la tabla

        if (ventas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="px-6 py-4 text-center text-gray-500">No hay ventas disponibles.</td></tr>`;
            return;
        }

        ventas.forEach(venta => {
            // Formatear la fecha a DD/MM/YYYY
            const fechaVenta = venta.fecha ? new Date(venta.fecha).toLocaleDateString('es-CO') : 'N/A';

            // Formatear precio y total con separadores de miles y símbolo COP
            const precioFormateado = venta.precio_kg ? `${parseFloat(venta.precio_kg).toLocaleString('es-CO')} COP/kg` : 'N/A';
            const totalFormateado = venta.total ? `${parseFloat(venta.total).toLocaleString('es-CO')} COP` : 'N/A';

            const row = `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${fechaVenta}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${venta.comprador || 'CafExport'}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                            ${venta.tipo_cafe || 'N/A'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        ${venta.cantidad || '0'} kg
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        ${precioFormateado}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        ${totalFormateado}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                            ${venta.estado || 'Pendiente'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">
                        <a href="#" class="text-gray-400 hover:text-gray-600 download-factura-btn" data-venta-id="${venta.id}">
                            <i class="fas fa-download"></i>
                        </a>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    }

    // Llamar a la función para obtener ventas al cargar la página
    fetchVentasCampesino();

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

            // Obtener valores de los inputs. Ya se convierten o limpian en otras partes del script si es necesario.
            let cantidad = parseFloat(document.getElementById('cantidad').value);
            let tipo_cafe = formData.get('tipo_cafe');
            let precio_kg = parseFloat(document.getElementById('precio_kg').value);

            // No es necesaria la limpieza adicional aquí si los valores ya están correctos en los inputs
            // if (cantidad) {
            //     cantidad = cantidad.replace(/[^0-9,-]/g, '').replace(',', '.');
            //     cantidad = parseFloat(cantidad);
            // }
            // if (precio_kg) {
            //     precio_kg = precio_kg.replace(/\./g, '').replace(',', '.');
            //     precio_kg = parseFloat(precio_kg);
            // }

            // Construir el objeto de datos para enviar al backend
            const dataToSend = {
                cantidad: cantidad,
                tipo_cafe: tipo_cafe,
                precio_kg: precio_kg
            };

            const jwtToken = localStorage.getItem('access_token');

            fetch('http://127.0.0.1:5000/api/ventas', { // Asegurarse de usar el puerto 5000
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
                console.log('Success:', data);
                alert(data.mensaje || 'Venta registrada con éxito');
                modal.classList.add('hidden');
                formRegistroVenta.reset(); // Resetear formulario
                updateTotal(); // Resetear el total mostrado
                fetchVentasCampesino(); // Actualizar la lista de ventas después de registrar una nueva
                
                // Llamar a la función para actualizar el dashboard
                updateDashboardDisplay();

            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Error al registrar la venta: ' + error.message);
            });

        } else {
            formRegistroVenta.reportValidity();
        }
    });

    // ** Nueva función para actualizar el dashboard **
    function updateDashboardDisplay() {
        const jwtToken = localStorage.getItem('access_token'); // Obtener el token JWT
        if (!jwtToken) {
            console.error('No JWT token found for dashboard update.');
            return; // Salir si no hay token
        }

        fetch('http://127.0.0.1:5000/api/campesino/dashboard', { // URL de la API del dashboard
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
            console.log('Datos del dashboard actualizados:', data);
            
            // Actualizar las tarjetas de estadísticas
            const totalVentasValueElement = document.getElementById('total-ventas-value');
            const completadasValueElement = document.getElementById('completadas-value');
            const pendientesValueElement = document.getElementById('pendientes-value');
            const totalIngresosValueElement = document.getElementById('total-ingresos-value');
            const promedioValueElement = document.getElementById('promedio-value');

            if (data.stats) {
                if (totalVentasValueElement && data.stats.total_ventas !== undefined) {
                    // Mostrar el número total de ventas (conteo)
                    totalVentasValueElement.innerText = `${data.stats.total_ventas.toLocaleString('es-CO')} COP`;
                }

                if (completadasValueElement && data.stats.completadas !== undefined) {
                    // Mostrar el número de ventas completadas
                    completadasValueElement.innerText = data.stats.completadas;
                }

                if (pendientesValueElement && data.stats.pendientes !== undefined) {
                    // Mostrar el número de ventas pendientes
                    pendientesValueElement.innerText = data.stats.pendientes;
                }

                if (totalIngresosValueElement && data.stats.total_ingresos !== undefined) {
                    // Mostrar el total de ingresos (suma) formateado como moneda COP
                    totalIngresosValueElement.innerText = `${parseFloat(data.stats.total_ingresos).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} COP`;
                }

                if (promedioValueElement && data.stats.promedio !== undefined) {
                    // Mostrar el promedio de ingresos formateado como moneda COP
                    promedioValueElement.innerText = `${parseFloat(data.stats.promedio).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} COP`;
                }
            }
            
            // Actualizar tabla de Ventas Recientes
            const recentSalesTableBody = document.querySelector('#recent-sales-table tbody');
            if (recentSalesTableBody && data.ventas_recientes) {
                populateRecentSalesTable(data.ventas_recientes);
            }

        })
        .catch(error => {
            console.error('Error updating dashboard:', error);
            // Mostrar mensaje de error en las tarjetas
            const totalVentasValueElement = document.getElementById('total-ventas-value');
            const completadasValueElement = document.getElementById('completadas-value');
            const pendientesValueElement = document.getElementById('pendientes-value');
            const totalIngresosValueElement = document.getElementById('total-ingresos-value');
            const promedioValueElement = document.getElementById('promedio-value');

            if (totalVentasValueElement) totalVentasValueElement.innerText = 'Error';
            if (completadasValueElement) completadasValueElement.innerText = 'Error';
            if (pendientesValueElement) pendientesValueElement.innerText = 'Error';
            if (totalIngresosValueElement) totalIngresosValueElement.innerText = 'Error';
            if (promedioValueElement) promedioValueElement.innerText = 'Error';
        });
    }

    // Función para poblar la tabla de ventas recientes
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

            const row = `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${fechaVenta}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${venta.comprador || 'CafExport'}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
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
                        <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                            ${venta.estado || 'Pendiente'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">
                        <a href="#" class="text-gray-400 hover:text-gray-600 download-factura-btn" data-venta-id="${venta.id}">
                            <i class="fas fa-download"></i>
                        </a>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    }
    
    // Si estás en la página del dashboard, llama a updateDashboardDisplay al cargar
    // (Puedes añadir una comprobación de URL o un flag en la plantilla)
     updateDashboardDisplay(); // Llamar a la función sin la restricción de URL

    // ** Nueva función para actualizar las estadísticas de ventas **
    // Esta función ahora calculará las estadísticas a partir de la lista de ventas
    function calculateAndDisplayStats(ventas) { 
        let totalVentasCount = 0;
        let completadasCount = 0;
        let pendientesCount = 0;
        let totalIngresosSum = 0.0;

        ventas.forEach(venta => {
            totalVentasCount++;
            if (venta.estado === 'Completada') { // Usar el valor exacto del enum de la BD
                completadasCount++;
            } else if (venta.estado === 'Pendiente') { // Usar el valor exacto del enum de la BD
                pendientesCount++;
            }
            // Asegurarse de que venta.total sea un número antes de sumarlo
            if (venta.total !== null && venta.total !== undefined) {
                 // Convertir el total a un número, manejando posibles strings si es necesario
                 const totalVenta = parseFloat(venta.total);
                 if (!isNaN(totalVenta)) {
                     totalIngresosSum += totalVenta;
                 }
            }
        });

        const promedioIngresos = totalVentasCount > 0 ? totalIngresosSum / totalVentasCount : 0.0;

        // Actualizar las tarjetas de estadísticas
        const totalVentasValueElement = document.getElementById('total-ventas-value');
        const completadasValueElement = document.getElementById('completadas-value');
        const pendientesValueElement = document.getElementById('pendientes-value');
        const totalIngresosValueElement = document.getElementById('total-ingresos-value');
        const promedioValueElement = document.getElementById('promedio-value');

        if (totalVentasValueElement) {
            totalVentasValueElement.innerText = totalVentasCount;
        }

        if (completadasValueElement) {
            completadasValueElement.innerText = completadasCount;
        }

        if (pendientesValueElement) {
            pendientesValueElement.innerText = pendientesCount;
        }

        if (totalIngresosValueElement) {
            // Formatear a COP con separadores de miles y dos decimales
            totalIngresosValueElement.innerText = `${totalIngresosSum.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} COP`;
        }

        if (promedioValueElement) {
            // Formatear a COP con separadores de miles y dos decimales
            promedioValueElement.innerText = `${promedioIngresos.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} COP`;
        }
    }

    // Función para descargar la factura
    async function downloadFactura(ventaId) {
        const jwtToken = localStorage.getItem('access_token');

        if (!jwtToken) {
            console.error('No JWT token found for factura download.');
            alert('Por favor, inicie sesión para descargar la factura.');
            window.location.href = '/campesino/login';
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:5000/api/ventas/${ventaId}/factura`, {
                method: 'GET',
                headers: {
                    'Authorization': 'Bearer ' + jwtToken,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                 const errorData = await response.json();
                 throw new Error(errorData.error || 'Error al descargar la factura');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            // Intentar obtener el nombre del archivo del encabezado Content-Disposition
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `factura_venta_${ventaId}.pdf`; // Nombre por defecto
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1];
                }
            }
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('Error downloading factura:', error);
            alert(`Error al descargar la factura: ${error.message}`);
        }
    }

    // Añadir event listener a la tabla para los botones de descarga
    const ventasTableBody = document.querySelector('#ventasTable tbody');
    if (ventasTableBody) {
        ventasTableBody.addEventListener('click', function(event) {
            const target = event.target;
            // Verificar si se hizo clic en el ícono o el enlace de descarga
            const downloadLink = target.closest('.download-factura-btn');
            if (downloadLink) {
                event.preventDefault(); // Prevenir el comportamiento por defecto del enlace
                const ventaId = downloadLink.getAttribute('data-venta-id');
                if (ventaId) {
                    downloadFactura(ventaId);
                }
            }
        });
    }
}); 