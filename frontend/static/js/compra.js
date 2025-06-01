// Archivo: frontend/static/js/compra.js

document.addEventListener('DOMContentLoaded', function() {
    const formRegistroCompra = document.getElementById('formRegistroCompra');
    const registrarCompraBtnModal = document.getElementById('registrarCompraBtnModal');
    const registroCompraModal = document.getElementById('registroCompraModal');
    const cerrarModalBtn = document.getElementById('cerrarModalBtn');
    const nuevaCompraBtn = document.getElementById('nuevaCompraBtn');
    const comprasTableBody = document.querySelector('#recent-sales-table tbody');
    const tablaContainer = document.getElementById('tabla-container');
    const tarjetasContainer = document.getElementById('tarjetas-container');

    // Elementos de las tarjetas de estadísticas
    const totalComprasCard = document.getElementById('total-compras-card');
    const completadasCard = document.getElementById('completadas-card');
    const enTransitoCard = document.getElementById('en-transito-card');
    const confirmadasCard = document.getElementById('confirmadas-card');
    const totalInversionCard = document.getElementById('total-inversion-card');
    const promedioCard = document.getElementById('promedio-card');

    // Función para obtener el token JWT
    function getJwtToken() {
        // Intentar obtener el token de diferentes fuentes
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
        console.log('Token obtenido:', token ? 'Token encontrado' : 'No hay token');
        return token;
    }

    // Función para verificar si el usuario está autenticado
    function checkAuth() {
        const token = getJwtToken();
        if (!token) {
            console.error('No se encontró el token de autenticación');
            alert('Por favor, inicie sesión para acceder a esta página');
            window.location.href = '/empresa/login';
            return false;
        }
        return true;
    }

    // Función para formatear números como moneda COP
    const formatCOP = (amount) => {
        return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(amount);
    };

    // Función para cargar y mostrar las estadísticas
    function loadEstadisticas() {
        if (!checkAuth()) return;

        const token = getJwtToken();
        console.log('Cargando estadísticas con token:', token ? 'Token presente' : 'Sin token');

        fetch('http://127.0.0.1:5000/empresa/estadisticas_compras', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    console.error('Token inválido o expirado');
                    alert('Su sesión ha expirado. Por favor, inicie sesión nuevamente.');
                    window.location.href = '/empresa/login';
                    return;
                }
                return response.text().then(text => {
                    console.error('Error en la respuesta:', text);
                    throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Estadísticas recibidas:', data);
            if (data.estadisticas) {
                const stats = data.estadisticas;
                // Actualizar el contenido de las tarjetas. Asegúrate de que los IDs coincidan.
                if(totalComprasCard) totalComprasCard.querySelector('p').textContent = stats.total_compras_count !== undefined ? stats.total_compras_count : '--';
                 if(totalComprasCard) { // Asumiendo que la cantidad total va en la misma tarjeta o cerca
                     const cantidadElement = totalComprasCard.querySelector('p:nth-of-type(2)'); // Ajusta el selector si es necesario
                     if(cantidadElement) cantidadElement.textContent = `Cantidad: ${stats.total_compras_cantidad !== undefined ? stats.total_compras_cantidad + ' kg' : '--'}`;
                     else if(totalComprasCard) totalComprasCard.innerHTML += `<p class="text-sm text-gray-600">Cantidad: ${stats.total_compras_cantidad !== undefined ? stats.total_compras_cantidad + ' kg' : '--'}</p>`;
                 }
                if(completadasCard) completadasCard.querySelector('p').textContent = stats.completadas_count !== undefined ? stats.completadas_count : '--';
                if(enTransitoCard) enTransitoCard.querySelector('p').textContent = stats.en_transito_count !== undefined ? stats.en_transito_count : '--';
                if(confirmadasCard) confirmadasCard.querySelector('p').textContent = stats.confirmadas_count !== undefined ? stats.confirmadas_count : '--';
                if(totalInversionCard) totalInversionCard.querySelector('p').textContent = stats.total_inversion !== undefined ? formatCOP(stats.total_inversion) + ' COP' : '-- COP';
                if(promedioCard) promedioCard.querySelector('p').textContent = stats.precio_promedio !== undefined ? formatCOP(stats.precio_promedio) + ' COP/kg' : '-- COP/kg';

            } else {
                 console.error('Error al cargar estadísticas: No se recibieron datos válidos.', data);
                 // Opcional: Mostrar un mensaje de error en las tarjetas
            }
        })
        .catch(error => {
            console.error('Error al cargar estadísticas:', error);
            // Opcional: Mostrar un mensaje de error en las tarjetas
        });
    }

    // Función para cargar y mostrar las compras (actualizada para vista de tabla y tarjetas)
    function loadCompras() {
        if (!checkAuth()) return;

        const token = getJwtToken();
        console.log('Cargando compras con token:', token ? 'Token presente' : 'Sin token');

        fetch('http://127.0.0.1:5000/empresa/compras', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    console.error('Token inválido o expirado');
                    alert('Su sesión ha expirado. Por favor, inicie sesión nuevamente.');
                    window.location.href = '/empresa/login';
                    return;
                }
                return response.text().then(text => {
                    console.error('Error en la respuesta:', text);
                    throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos de compras recibidos:', data); // Debug
            comprasTableBody.innerHTML = ''; // Limpiar la tabla actual
            tarjetasContainer.innerHTML = ''; // Limpiar el contenedor de tarjetas actual

            if (data.compras && data.compras.length > 0) {
                data.compras.forEach(compra => {
                    console.log('Procesando compra:', compra); // Debug
                    
                    // Generar fila de tabla
                    const tableRow = `
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ${compra.fecha_orden ? new Date(compra.fecha_orden).toLocaleDateString() : 'N/A'}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                <div class="flex items-center">
                                    <div class="flex-shrink-0 h-8 w-8 rounded-full bg-green-200 flex items-center justify-center text-sm font-medium text-green-800">
                                        ${compra.vendedor_nombre ? compra.vendedor_nombre.charAt(0) : 'C'}
                                    </div>
                                    <div class="ml-4">
                                        <div class="text-sm font-medium text-gray-900">${compra.vendedor_nombre || 'CafExport'}</div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${compra.tipo_cafe === 'Arabica' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'}">
                                    ${compra.tipo_cafe || 'N/A'}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ${compra.cantidad ? parseFloat(compra.cantidad).toFixed(2) + ' kg' : 'N/A'}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ${compra.precio_kg ? formatCOP(parseFloat(compra.precio_kg)) + '/kg' : 'N/A'}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ${compra.total ? formatCOP(parseFloat(compra.total)) : 'N/A'}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getEstadoClass(compra.estado)}">
                                    ${compra.estado || 'N/A'}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <button class="text-gray-400 hover:text-gray-600 download-factura-btn" data-id="${compra.id}" title="Descargar Factura">
                                    <i class="fas fa-download"></i>
                                </button>
                                <button class="text-gray-400 hover:text-gray-600 view-details-btn" data-id="${compra.id}" title="Ver Detalles">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                            </td>
                        </tr>
                    `;
                    comprasTableBody.innerHTML += tableRow;

                    // Generar tarjeta
                    const card = `
                        <div class="bg-white rounded-lg shadow p-4">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-sm text-gray-500">Fecha: ${compra.fecha_orden ? new Date(compra.fecha_orden).toLocaleDateString() : 'N/A'}</span>
                                <span class="px-2 py-1 text-xs leading-5 font-semibold rounded-full ${getEstadoClass(compra.estado)}">
                                    ${compra.estado || 'N/A'}
                                </span>
                            </div>
                            <div class="font-medium text-gray-900 mb-2">${compra.tipo_cafe || 'N/A'} - ${compra.cantidad ? parseFloat(compra.cantidad).toFixed(2) + ' kg' : 'N/A'}</div>
                            <div class="text-sm text-gray-600 mb-2">Proveedor: ${compra.vendedor_nombre || 'CafExport'}</div>
                            <div class="flex justify-between items-center">
                                <span class="text-lg font-semibold text-green-800">${compra.total ? formatCOP(parseFloat(compra.total)) : 'N/A'}</span>
                                <div class="flex space-x-2 items-center">
                                     <button class="text-gray-400 hover:text-gray-600 download-factura-btn" data-id="${compra.id}" title="Descargar Factura">
                                        <i class="fas fa-download"></i>
                                    </button>
                                    <button class="text-gray-400 hover:text-gray-600 view-details-btn" data-id="${compra.id}" title="Ver Detalles">
                                        <i class="fas fa-ellipsis-v"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                    tarjetasContainer.innerHTML += card;
                });
            } else {
                const noResultsHtml = '<tr><td colspan="8" class="px-6 py-4 text-center text-gray-500">No hay compras registradas.</td></tr>';
                comprasTableBody.innerHTML = noResultsHtml;
                tarjetasContainer.innerHTML = '<p class="text-center text-gray-500">No hay compras registradas.</p>';
            }
        })
        .catch(error => {
            console.error('Error al cargar las compras:', error);
            const errorHtml = '<tr><td colspan="8" class="px-6 py-4 text-center text-red-500">Error al cargar las compras. Por favor, intente nuevamente.</td></tr>';
            comprasTableBody.innerHTML = errorHtml;
            tarjetasContainer.innerHTML = '<p class="text-center text-red-500">Error al cargar las compras. Por favor, intente nuevamente.</p>';
        });
    }

    // Función auxiliar para determinar la clase CSS según el estado
    function getEstadoClass(estado) {
        switch(estado) {
            case 'Completada':
                return 'bg-green-100 text-green-800';
            case 'Pendiente':
                return 'bg-yellow-100 text-yellow-800';
            case 'Aprobada':
                return 'bg-blue-100 text-blue-800';
            case 'Rechazada':
                return 'bg-red-100 text-red-800';
            case 'Cancelada':
                return 'bg-gray-100 text-gray-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    }

    // Función para ver detalles de una compra (placeholder)
    function verDetallesCompra(id) {
        console.log('Ver detalles de compra:', id);
        // Implementar lógica para mostrar detalles
    }

    // Función para descargar la factura de una compra
    async function downloadFacturaCompra(compraId) {
        if (!checkAuth()) return;

        const token = getJwtToken();
        if (!token) {
            console.error('No JWT token found for invoice download.');
            alert('Por favor, inicie sesión para descargar facturas.');
            return;
        }

        try {
            console.log(`Attempting to download invoice for purchase ID: ${compraId}`);
            // Asumo que la URL en el backend será /empresa/compras/<compra_id>/factura
            const response = await fetch(`http://127.0.0.1:5000/empresa/compras/${compraId}/factura`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                }
            });

            console.log('Invoice response status:', response.status);

            if (!response.ok) {
                 const errorData = await response.json();
                 console.error('Error downloading invoice:', errorData);
                 throw new Error(errorData.error || errorData.message || 'Error al descargar la factura.');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            // Intenta obtener el nombre del archivo del encabezado Content-Disposition
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `factura_compra_${compraId}.pdf`;
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
            console.error('Error downloading invoice:', error);
            alert(`Error al descargar la factura: ${error.message}`);
        }
    }

    // Event listener para los botones de descarga de factura
    // Usamos delegación de eventos en el cuerpo de la tabla
    if (comprasTableBody) {
        comprasTableBody.addEventListener('click', function(event) {
            const target = event.target.closest('.download-factura-btn');
            if (target) {
                const compraId = target.dataset.id;
                if (compraId) {
                    downloadFacturaCompra(compraId);
                }
            }
        });
    }

    // Función para abrir el modal
    function abrirModal() {
        console.log('Abriendo modal...');
        registroCompraModal.classList.remove('hidden');
        // Resetear el formulario cada vez que se abre el modal
        if (formRegistroCompra) {
            formRegistroCompra.reset();
             // Disparar el evento change en tipo_cafe para actualizar precio/total al abrir el modal
            const tipoCafeSelect = document.getElementById('tipo_cafe');
            if (tipoCafeSelect) {
                tipoCafeSelect.dispatchEvent(new Event('change'));
            }
        }
    }

    // Función para cerrar el modal
    function cerrarModal() {
        console.log('Cerrando modal...');
        registroCompraModal.classList.add('hidden');
        if (formRegistroCompra) {
            formRegistroCompra.reset();
        }
    }

    // Event listeners para el modal
    if (nuevaCompraBtn) {
        console.log('Añadiendo listener al botón Nueva Compra');
        nuevaCompraBtn.addEventListener('click', abrirModal);
    }

    if (cerrarModalBtn) {
        console.log('Añadiendo listener al botón Cerrar');
        cerrarModalBtn.addEventListener('click', cerrarModal);
    }

    // Cerrar modal al hacer clic fuera de él
    if (registroCompraModal) {
        registroCompraModal.addEventListener('click', function(e) {
            if (e.target === registroCompraModal) {
                cerrarModal();
            }
        });
    }

    if (formRegistroCompra && registrarCompraBtnModal && registroCompraModal) {
        registrarCompraBtnModal.addEventListener('click', function(event) {
            event.preventDefault();
            if (!checkAuth()) return;

            const formData = new FormData(formRegistroCompra);
            const compraData = {};
            formData.forEach((value, key) => {
                compraData[key] = value;
            });

            // Validación básica en el frontend (el backend también valida)
            if (!compraData.fecha_orden || !compraData.tipo_cafe || !compraData.cantidad || !compraData.precio_kg) {
                alert('Por favor, complete todos los campos obligatorios.');
                return;
            }
            
            // Asegurarse de enviar el precio_kg calculado, no el formateado si se mostrara así
            compraData.precio_kg = parseFloat(document.getElementById('precio_kg').value);

             const token = getJwtToken();
             if (!token) {
                console.error('No se encontró el token JWT. No se puede registrar la compra.');
                alert('Error de autenticación. Por favor, inicie sesión de nuevo.');
                return;
             }

            // Corregir la URL para que apunte al backend
            fetch('http://127.0.0.1:5000/empresa/registrar_compra', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                credentials: 'include',
                body: JSON.stringify(compraData)
            })
            .then(response => {
                 if (!response.ok) {
                     if (response.status === 401) {
                         console.error('Token inválido o expirado');
                         alert('Su sesión ha expirado. Por favor, inicie sesión nuevamente.');
                         window.location.href = '/empresa/login';
                         return;
                     }
                     return response.text().then(text => { throw new Error(`HTTP error! status: ${response.status}, body: ${text}`); });
                 }
                 return response.json();
            })
            .then(data => {
                 console.log('Respuesta de registro de compra:', data);
                if (data.message === 'Compra registrada con éxito') {
                    alert(data.message);
                    loadEstadisticas();
                    loadCompras();
                    cerrarModal();
                } else {
                    // Mostrar mensajes de error específicos del backend si están disponibles
                    const errorMessage = data.message || 'Error al registrar la compra.';
                    alert('Error al registrar la compra: ' + errorMessage);
                }
            })
            .catch(error => {
                console.error('Error al enviar la solicitud de registro:', error);
                alert('Ocurrió un error de conexión al registrar la compra.');
            });
        });
    }

    // --- Funcionalidad de Vista de Tabla/Tarjetas ---
    const vistaTablaBtn = document.querySelector('.bg-gray-100 button:first-child'); 
    const vistaTarjetasBtn = document.querySelector('.bg-gray-100 button:last-child'); 
    
    // Asegúrate de que estos elementos existen antes de añadir listeners
    if (vistaTablaBtn && vistaTarjetasBtn && tablaContainer && tarjetasContainer) {
        vistaTablaBtn.addEventListener('click', function() {
            // Activar botón de tabla y desactivar botón de tarjetas
            vistaTablaBtn.classList.add('bg-white', 'text-gray-800', 'shadow');
            vistaTablaBtn.classList.remove('text-gray-600');
            vistaTarjetasBtn.classList.remove('bg-white', 'text-gray-800', 'shadow');
            vistaTarjetasBtn.classList.add('text-gray-600');

            // Mostrar tabla y ocultar tarjetas
            tablaContainer.classList.remove('hidden');
            tarjetasContainer.classList.add('hidden');
        });

        vistaTarjetasBtn.addEventListener('click', function() {
            // Activar botón de tarjetas y desactivar botón de tabla
            vistaTarjetasBtn.classList.add('bg-white', 'text-gray-800', 'shadow');
            vistaTarjetasBtn.classList.remove('text-gray-600');
            vistaTablaBtn.classList.remove('bg-white', 'text-gray-800', 'shadow');
            vistaTablaBtn.classList.add('text-gray-600');

            // Ocultar tabla y mostrar tarjetas
            tablaContainer.classList.add('hidden');
            tarjetasContainer.classList.remove('hidden');
        });
         // Establecer la vista inicial a Tabla al cargar la página
         vistaTablaBtn.click();
    }

    // Función para inicializar los datos de la página (ahora carga estadísticas, compras y precios de la API)
    function initPageData() {
        console.log('Iniciando carga de datos de la página de compras de empresa...');
        loadEstadisticas(); // Cargar estadísticas
        loadCompras(); // Cargar historial de compras
        fetchCafePrices(); // Cargar precios del café usando la nueva lógica
    }

    // Cargar datos al iniciar la página
    initPageData();

    // Objeto para almacenar los precios del café obtenidos de la API (ahora de la API de scraping via backend)
    let localCafePrices = {};
    // Variables para almacenar los precios por Kg calculados
    let precioArabicaKg = 0;
    let precioPasillaKg = 0;

    // Función para obtener los precios del café desde la API (ahora llama a /empresa/precios_cafe)
    async function fetchCafePrices() {
        try {
            // Llamar a la API de precios de la empresa (que ahora llama a la API de scraping)
            const response = await fetch('http://127.0.0.1:5000/empresa/precios_cafe');
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
            }
            const data = await response.json();
            console.log('Datos de precios recibidos de /empresa/precios_cafe:', data); // Debug

            // Procesar los precios recibidos (vienen como strings con formato)
            const precioArabicaStr = data.arabica || '0';
            const precioPasillaStr = data.pasilla || '0';

            // Limpiar y convertir a números
            // Eliminar caracteres no numéricos excepto el punto/coma decimal si aplica (aunque la API de ventas devuelve puntos de miles)
             const cleanPrecioArabica = precioArabicaStr.replace(/[^0-9]/g, ''); // Elimina todo excepto dígitos
             const cleanPrecioPasilla = precioPasillaStr.replace(/[^0-9]/g, ''); // Elimina todo excepto dígitos

             const precioArabicaCarga = parseFloat(cleanPrecioArabica);
             const precioPasillaArroba = parseFloat(cleanPrecioPasilla);

             console.log('Precios limpiados y parseados:', { precioArabicaCarga, precioPasillaArroba });

             // Calcular precio por Kg (1 carga = 125kg, 1 arroba = 12.5kg)
            if (!isNaN(precioArabicaCarga) && precioArabicaCarga > 0) {
                precioArabicaKg = precioArabicaCarga / 125; // Precio por carga (125kg)
            }
             if (!isNaN(precioPasillaArroba) && precioPasillaArroba > 0) {
                precioPasillaKg = precioPasillaArroba / 12.5; // Precio por arroba (12.5kg)
            }

            console.log('Precios calculados por Kg para empresa:', { precioArabicaKg, precioPasillaKg });

            // Almacenar los precios por kg calculados localmente (o si la API devolviera directamente el precio/kg)
            localCafePrices = {
                'arabica': precioArabicaKg,
                'pasilla': precioPasillaKg
            };

            // Actualizar los elementos de precio en la página de compras de empresa
            const precioCafeCargaElement = document.getElementById('precio-cafe-carga');
            const precioPasillaElement = document.getElementById('precio-pasilla');
            const fechaPrecioCargaElement = document.getElementById('fecha-precio-carga'); // Asumimos que hay un elemento para la fecha
            const fechaPrecioPasillaElement = document.getElementById('fecha-precio-pasilla'); // Asumimos que hay un elemento para la fecha

            if (precioCafeCargaElement && data.arabica !== undefined) {
                 // Formatear el precio de la CARGA para mostrar en la tarjeta
                 const precioCargaMostrar = parseFloat(cleanPrecioArabica);
                 if (!isNaN(precioCargaMostrar)) {
                     precioCafeCargaElement.innerText = `$${precioCargaMostrar.toLocaleString('es-CO')}`;
                 } else {
                     precioCafeCargaElement.innerText = 'N/A';
                 }
            }
            if (precioPasillaElement && data.pasilla !== undefined) {
                 // Formatear el precio de la ARROBA para mostrar en la tarjeta
                 const precioPasillaMostrar = parseFloat(cleanPrecioPasilla);
                  if (!isNaN(precioPasillaMostrar)) {
                     precioPasillaElement.innerText = `$${precioPasillaMostrar.toLocaleString('es-CO')}`;
                 } else {
                     precioPasillaElement.innerText = 'N/A';
                  }
            }

            // Actualizar fecha de actualización (usando la fecha de la API si está disponible)
            const fechaActualizacion = data.fecha_actualizacion;
            if (fechaPrecioCargaElement && fechaActualizacion) {
                try {
                    const fecha = new Date(fechaActualizacion);
                    const formattedDate = fecha.toLocaleDateString('es-CO', { day: '2-digit', month: '2-digit', year: 'numeric' });
                    fechaPrecioCargaElement.innerText = `Actualizado al ${formattedDate}`;
                    // Si hay un elemento de fecha separado para pasilla, actualízalo también
                    if (fechaPrecioPasillaElement) {
                        fechaPrecioPasillaElement.innerText = `Actualizado al ${formattedDate}`;
                    }
                } catch (e) {
                    console.error('Error parsing date from API:', e);
                     if (fechaPrecioCargaElement) fechaPrecioCargaElement.innerText = 'Fecha no disponible';
                     if (fechaPrecioPasillaElement) fechaPrecioPasillaElement.innerText = 'Fecha no disponible';
                }
            } else {
                 if (fechaPrecioCargaElement) fechaPrecioCargaElement.innerText = 'Fecha no disponible';
                 if (fechaPrecioPasillaElement) fechaPrecioPasillaElement.innerText = 'Fecha no disponible';
            }


            // Una vez que los precios se cargan y calculan, actualizar el precio en el modal
            // si ya hay un tipo seleccionado (ej. si el modal se abrió antes de que cargaran los precios)
            updatePrecioKg();

        } catch (error) {
            console.error('Error al obtener precios de café de la API de empresa:', error);
            // Manejar el error: quizás deshabilitar la selección de tipo de café o mostrar un mensaje
             const precioCafeCargaElement = document.getElementById('precio-cafe-carga');
             const precioPasillaElement = document.getElementById('precio-pasilla');
             const fechaPrecioCargaElement = document.getElementById('fecha-precio-carga');
             const fechaPrecioPasillaElement = document.getElementById('fecha-precio-pasilla');

             if (precioCafeCargaElement) precioCafeCargaElement.innerText = 'Error';
             if (precioPasillaElement) precioPasillaElement.innerText = 'Error';
             if (fechaPrecioCargaElement) fechaPrecioCargaElement.innerText = 'Error al cargar';
             if (fechaPrecioPasillaElement) fechaPrecioPasillaElement.innerText = 'Error al cargar';

            // Opcional: Limpiar los inputs de precio y total en el modal si falla la carga
             const tipoCafeSelectModal = document.getElementById('tipo_cafe');
             const precioKgInputModal = document.getElementById('precio_kg');
             const totalCompraInputModal = document.getElementById('total_compra');
             if (tipoCafeSelectModal) tipoCafeSelectModal.disabled = true; // Deshabilitar selección si no hay precios
             if (precioKgInputModal) precioKgInputModal.value = '';
             if (totalCompraInputModal) totalCompraInputModal.value = '';
        }
    }

    // Función para actualizar el precio por kg basado en el tipo de café seleccionado en el modal
    function updatePrecioKg() {
        const tipoCafeSelectModal = document.getElementById('tipo_cafe');
        const precioKgInputModal = document.getElementById('precio_kg');

        if (!tipoCafeSelectModal || !precioKgInputModal) return; // Salir si los elementos no existen

        const selectedTipo = tipoCafeSelectModal.value;
        let precio = undefined;

        // Buscar el precio por kg calculado en los precios cargados localmente
        if (selectedTipo === 'Arabica') {
             precio = localCafePrices['arabica'];
        } else if (selectedTipo === 'Pasilla') {
             precio = localCafePrices['pasilla'];
        }

        if (precio !== undefined) {
            precioKgInputModal.value = precio.toFixed(2); // Mostrar con 2 decimales
        } else {
            precioKgInputModal.value = ''; // Limpiar si no se encuentra el precio para el tipo seleccionado
            console.warn(`Precio por kg para ${selectedTipo} no encontrado en localCafePrices.`);
        }
        // Siempre actualizar el total después de actualizar el precio por kg
        updateTotal();
    }

    // Función para calcular y actualizar el total de la compra en el modal
    function updateTotal() {
         const cantidadInputModal = document.getElementById('cantidad');
         const precioKgInputModal = document.getElementById('precio_kg');
         const totalCompraInputModal = document.getElementById('total_compra');

         if (!cantidadInputModal || !precioKgInputModal || !totalCompraInputModal) return; // Salir si los elementos no existen

        const cantidad = parseFloat(cantidadInputModal.value);
        const precioKg = parseFloat(precioKgInputModal.value);
        const total = (cantidad && precioKg) ? cantidad * precioKg : 0;

        totalCompraInputModal.value = total.toFixed(2); // Formatear a 2 decimales para el input
    }

    // Event listeners para actualizar precio y total en el modal
    const tipoCafeSelectModal = document.getElementById('tipo_cafe');
    const cantidadInputModal = document.getElementById('cantidad');
    const precioKgInputModal = document.getElementById('precio_kg');

     if (tipoCafeSelectModal) tipoCafeSelectModal.addEventListener('change', updatePrecioKg);
     if (cantidadInputModal) cantidadInputModal.addEventListener('input', updateTotal);
     // aunque precioKgInput es readonly, mantenemos el listener por si acaso o para depuración
     if (precioKgInputModal) precioKgInputModal.addEventListener('input', updateTotal);

});

// Asegúrate de que estas funciones estén disponibles globalmente si se llaman desde el HTML
// window.verDetallesCompra = verDetallesCompra; 