document.addEventListener('DOMContentLoaded', function() {
    // Función para obtener el token JWT
    function getJwtToken() {
        // Intentar obtener el token de diferentes fuentes (localStorage, sessionStorage)
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
        // console.log('Token obtenido para dashboard:', token ? 'Token encontrado' : 'No hay token'); // Debug
        return token;
    }

    // Función para verificar autenticación y redirigir si no hay token
    function checkAuthAndRedirect() {
        const token = getJwtToken();
        if (!token) {
            console.error('No se encontró el token de autenticación para el dashboard.');
            // alert('Su sesión ha expirado o no ha iniciado sesión. Por favor, inicie sesión de nuevo.'); // Evitar alerts automáticos en carga
            // Redirigir solo si no estamos ya en la página de login (para evitar bucles)
            if (!window.location.pathname.includes('/empresa/login')) {
                 window.location.href = '/empresa/login'; // Ajusta esta URL si es diferente
            }
            return false;
        }
        return true;
    }

    // Verificar autenticación al cargar la página
    if (!checkAuthAndRedirect()) {
        return; // Detener la ejecución si no está autenticado
    }

    // Función para formatear números como moneda COP
    const formatCOP = (amount) => {
         if (amount === null || amount === undefined) return '--';
         const numberAmount = parseFloat(amount);
         if (isNaN(numberAmount)) return '--';
        return `$${numberAmount.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
    };

     // Función para formatear números con decimales si es necesario (e.g., cantidad)
    const formatNumber = (amount, decimals = 0) => {
         if (amount === null || amount === undefined) return '--';
         const numberAmount = parseFloat(amount);
         if (isNaN(numberAmount)) return '--';
        return numberAmount.toLocaleString('es-CO', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    };

    // Función para calcular y mostrar las estadísticas
    function loadEstadisticas() {
        const token = getJwtToken();
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
                 if (response.status === 401) { // Token inválido o expirado
                     checkAuthAndRedirect(); // Redirigir
                     return Promise.reject('Token inválido o expirado'); // Rechazar para evitar seguir procesando
                 }
                return response.text().then(text => { throw new Error(`HTTP error! status: ${response.status}, body: ${text}`); });
            }
            return response.json();
        })
        .then(data => {
            console.log('Estadísticas recibidas:', data);
            if (data.estadisticas) {
                const stats = data.estadisticas;
                document.getElementById('total-compras-value').innerText = formatCOP(stats.total_inversion);
                 // Ajusta este texto según lo que signifique la estadística de cantidad total
                 // Si total_compras_cantidad es el total en kg:
                document.getElementById('total-compras-period').innerText = `Cantidad total: ${formatNumber(stats.total_compras_cantidad, 2)} kg`;
                 // Si stats.total_compras_count es el número de compras:
                 // document.getElementById('total-compras-period').innerText = `${stats.total_compras_count} compras realizadas`;

                // Actualizar la próxima entrega
                if (stats.proxima_entrega.fecha) {
                    document.getElementById('proxima-entrega-date').innerText = stats.proxima_entrega.fecha;
                    document.getElementById('proxima-entrega-days').innerText = stats.proxima_entrega.dias !== null ? `Faltan ${stats.proxima_entrega.dias} días` : 'No hay próximas entregas';
                } else {
                    document.getElementById('proxima-entrega-date').innerText = 'No hay próximas entregas';
                    document.getElementById('proxima-entrega-days').innerText = '';
                }

            } else {
                 console.error('Error al cargar estadísticas: No se recibieron datos válidos.', data);
                 // Mostrar indicación de error en el UI
                  document.getElementById('total-compras-value').innerText = 'Error';
                  document.getElementById('total-compras-period').innerText = 'Error';
                  document.getElementById('proxima-entrega-date').innerText = 'Error';
                  document.getElementById('proxima-entrega-days').innerText = 'Error';
            }
        })
        .catch(error => {
            console.error('Error al cargar estadísticas:', error);
            // Mostrar indicación de error en el UI
             document.getElementById('total-compras-value').innerText = 'Error';
             document.getElementById('total-compras-period').innerText = 'Error';
             document.getElementById('proxima-entrega-date').innerText = 'Error';
             document.getElementById('proxima-entrega-days').innerText = 'Error';
        });
    }

    // Función para cargar y mostrar las compras recientes
    function loadComprasRecientes() {
         const token = getJwtToken();
         fetch('http://127.0.0.1:5000/empresa/compras', { // Obtiene todas las compras
             method: 'GET',
             headers: {
                 'Authorization': `Bearer ${token}`,
                 'Content-Type': 'application/json'
             },
             credentials: 'include'
         })
         .then(response => {
             if (!response.ok) {
                  if (response.status === 401) { // Token inválido o expirado
                      checkAuthAndRedirect(); // Redirigir
                      return Promise.reject('Token inválido o expirado'); // Rechazar para evitar seguir procesando
                  }
                 return response.text().then(text => { throw new Error(`HTTP error! status: ${response.status}, body: ${text}`); });
             }
             return response.json();
         })
         .then(data => {
             console.log('Datos de compras recibidos:', data); // Debug
             const comprasListElement = document.getElementById('compras-recientes-list');
             if (!comprasListElement) return; // Asegurar que el elemento existe
             comprasListElement.innerHTML = ''; // Limpiar lista actual

             if (data.compras && data.compras.length > 0) {
                 // Tomar las 3 compras más recientes (ajusta el número si es necesario)
                 const comprasRecientes = data.compras.slice(0, 3);

                 document.getElementById('compras-recientes-info').innerText = `Has realizado ${data.compras.length} compras en total. Mostrando las ${comprasRecientes.length} más recientes.`;

                 comprasRecientes.forEach(compra => {
                     const compraItemHtml = `
                         <div class="flex items-center justify-between py-3 border-b">
                             <div class="flex items-center">
                                 <i class="fas fa-coffee text-green-600 bg-green-100 p-2 rounded-full mr-4"></i>
                                 <div>
                                     <p class="font-medium">Café ${compra.tipo_cafe || 'N/A'} - ${formatNumber(compra.cantidad, 0)} kg</p>
                                     <p class="text-sm text-gray-500">${compra.fecha_orden ? new Date(compra.fecha_orden).toLocaleDateString('es-CO') : 'N/A'} - Proveedor: ${compra.vendedor_nombre || 'CafExport'}</p>
                                 </div>
                             </div>
                             <div class="text-right">
                                 <span class="${getEstadoClass(compra.estado)} px-2 py-1 rounded text-sm">${compra.estado || 'N/A'}</span>
                                 <p class="text-lg font-semibold mt-1">${formatCOP(compra.total)} COP</p>
                             </div>
                         </div>
                     `;
                     comprasListElement.innerHTML += compraItemHtml;
                 });
             } else {
                  document.getElementById('compras-recientes-info').innerText = 'No hay compras recientes.';
                 comprasListElement.innerHTML = '<p class="text-center text-gray-500">No hay compras recientes registradas.</p>';
             }
         })
         .catch(error => {
             console.error('Error al cargar compras recientes:', error);
             const comprasListElement = document.getElementById('compras-recientes-list');
              if (comprasListElement) {
                 comprasListElement.innerHTML = '<p class="text-center text-red-500">Error al cargar compras recientes.</p>';
                  document.getElementById('compras-recientes-info').innerText = 'Error al cargar.';
              }
         });
    }

     // Función auxiliar para determinar la clase CSS del estado (basada en Enum)
    function getEstadoClass(estado) {
         switch(estado) {
             case 'Completada':
                 return 'bg-green-100 text-green-800';
             case 'Pendiente':
                 return 'bg-yellow-100 text-yellow-800';
             case 'Confirmadas': // Usar 'Confirmadas' para las compras
                 return 'bg-blue-100 text-blue-800';
             case 'Rechazada': // Aunque no se use en compras, está en el ENUM de ventas
                 return 'bg-red-100 text-red-800';
             case 'Cancelada': // Aunque no se use en compras, está en el ENUM de ventas
                 return 'bg-gray-100 text-gray-800';
             default:
                 return 'bg-gray-100 text-gray-800';
         }
     }


    // Función para cargar y mostrar los precios actuales del mercado
    function loadPreciosMercado() {
         fetch('http://127.0.0.1:5000/empresa/precios_cafe', { // Llama a la API que hace scraping
             method: 'GET',
             headers: { 'Content-Type': 'application/json' } // No necesita token para esta API pública
         })
         .then(response => {
             if (!response.ok) {
                  return response.text().then(text => { throw new Error(`HTTP error! status: ${response.status}, body: ${text}`); });
             }
             return response.json();
         })
         .then(data => {
             console.log('Datos de precios de mercado recibidos:', data); // Debug

             const precioActualizacionFechaElement = document.getElementById('precios-actualizacion-fecha');
             const precioArabicaKgElement = document.getElementById('precio-arabica-kg');
             const precioArabicaCargaElement = document.getElementById('precio-arabica-carga');
             const precioPasillaKgElement = document.getElementById('precio-pasilla-kg');
             const precioPasillaArrobaElement = document.getElementById('precio-pasilla-arroba');

             // Procesar los precios recibidos (vienen como strings con formato de la API de scraping)
             const precioArabicaStr = data.arabica || 'N/A';
             const precioPasillaStr = data.pasilla || 'N/A';
             const fechaActualizacion = data.fecha_actualizacion;

             // Calcular precios por Kg y por unidad si los datos están disponibles
             let precioArabicaKg = 'N/A';
             let precioArabicaCarga = 'N/A';
             let precioPasillaKg = 'N/A';
             let precioPasillaArroba = 'N/A';

             if (precioArabicaStr !== 'N/A') {
                  // Limpiar el string para obtener el número (elimina '$' y '.')
                 const cleanPrecioArabica = precioArabicaStr.replace(/[^0-9]/g, '');
                 const numPrecioArabicaCarga = parseFloat(cleanPrecioArabica);
                 if (!isNaN(numPrecioArabicaCarga) && numPrecioArabicaCarga > 0) {
                     // Mostrar precio por Carga (el valor crudo de la API)
                     precioArabicaCarga = formatCOP(numPrecioArabicaCarga); // Formatear a COP
                     // Calcular precio por Kg (asumiendo 1 carga = 125kg)
                     precioArabicaKg = formatCOP(numPrecioArabicaCarga / 125) + '/kg'; // Formatear a COP/kg
                 }
             }

              if (precioPasillaStr !== 'N/A') {
                  // Limpiar el string para obtener el número (elimina '$' y '.')
                 const cleanPrecioPasilla = precioPasillaStr.replace(/[^0-9]/g, '');
                 const numPrecioPasillaArroba = parseFloat(cleanPrecioPasilla);
                  if (!isNaN(numPrecioPasillaArroba) && numPrecioPasillaArroba > 0) {
                      // Mostrar precio por Arroba (el valor crudo de la API)
                      precioPasillaArroba = formatCOP(numPrecioPasillaArroba); // Formatear a COP
                      // Calcular precio por Kg (asumiendo 1 arroba = 12.5kg)
                      precioPasillaKg = formatCOP(numPrecioPasillaArroba / 12.5) + '/kg'; // Formatear a COP/kg
                  }
              }

             // Actualizar los elementos en el HTML
             if (precioArabicaKgElement) precioArabicaKgElement.innerText = precioArabicaKg;
             if (precioArabicaCargaElement) precioArabicaCargaElement.innerText = precioArabicaCarga;
             if (precioPasillaKgElement) precioPasillaKgElement.innerText = precioPasillaKg;
             if (precioPasillaArrobaElement) precioPasillaArrobaElement.innerText = precioPasillaArroba;

             // Actualizar fecha de actualización
             if (precioActualizacionFechaElement && fechaActualizacion) {
                 try {
                     const fecha = new Date(fechaActualizacion);
                      // Formato similar al de la imagen (dd de mes, aaaa)
                     const options = { day: 'numeric', month: 'long', year: 'numeric' };
                     precioActualizacionFechaElement.innerText = `Precios actualizados al ${fecha.toLocaleDateString('es-ES', options)}`;
                 } catch (e) {
                     console.error('Error parsing date for market prices:', e);
                     precioActualizacionFechaElement.innerText = 'Fecha de actualización no disponible';
                 }
             } else if (precioActualizacionFechaElement) {
                  precioActualizacionFechaElement.innerText = 'Fecha de actualización no disponible';
             }

         })
         .catch(error => {
             console.error('Error al cargar precios de mercado:', error);
             // Mostrar indicación de error en el UI
              if (document.getElementById('precios-actualizacion-fecha')) document.getElementById('precios-actualizacion-fecha').innerText = 'Error al cargar precios';
              if (document.getElementById('precio-arabica-kg')) document.getElementById('precio-arabica-kg').innerText = 'Error';
              if (document.getElementById('precio-arabica-carga')) document.getElementById('precio-arabica-carga').innerText = 'Error';
              if (document.getElementById('precio-pasilla-kg')) document.getElementById('precio-pasilla-kg').innerText = 'Error';
              if (document.getElementById('precio-pasilla-arroba')) document.getElementById('precio-pasilla-arroba').innerText = 'Error';
         });
    }

    // Lógica para el manejo de pestañas (Compras Recientes vs Reportes)
    function setupTabs() {
        const tabsContainer = document.getElementById('dashboard-tabs');
        const comprasRecientesTabLink = tabsContainer ? tabsContainer.querySelector('a[data-tab="compras-recientes"]') : null;
        const reportesTabLink = tabsContainer ? tabsContainer.querySelector('a[data-tab="reportes"]') : null;
        const comprasRecientesTabContent = document.getElementById('compras-recientes-tab');
        const reportesTabContent = document.getElementById('reportes-tab');

        if (!tabsContainer || !comprasRecientesTabLink || !reportesTabLink || !comprasRecientesTabContent || !reportesTabContent) {
            console.warn('Elementos de pestañas no encontrados.');
            return; // Salir si no se encuentran los elementos necesarios
        }

        // Mostrar la pestaña correcta al cargar (compras recientes por defecto)
        showTab('compras-recientes');

        // Añadir event listeners a los enlaces de las pestañas
        comprasRecientesTabLink.addEventListener('click', function(event) {
            event.preventDefault();
            showTab('compras-recientes');
        });

        reportesTabLink.addEventListener('click', function(event) {
            event.preventDefault();
            showTab('reportes');
        });

        // Función para mostrar/ocultar pestañas
        function showTab(tabId) {
            // Remover clase activa de todos los enlaces
            comprasRecientesTabLink.classList.remove('border-green-600', 'text-green-600');
            comprasRecientesTabLink.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700');
            reportesTabLink.classList.remove('border-green-600', 'text-green-600');
            reportesTabLink.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700');

            // Ocultar todo el contenido de las pestañas
            comprasRecientesTabContent.classList.add('hidden');
            reportesTabContent.classList.add('hidden');

            // Mostrar la pestaña seleccionada y activar su enlace
            if (tabId === 'compras-recientes') {
                comprasRecientesTabContent.classList.remove('hidden');
                comprasRecientesTabLink.classList.add('border-green-600', 'text-green-600');
                comprasRecientesTabLink.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700');
            } else if (tabId === 'reportes') {
                reportesTabContent.classList.remove('hidden');
                reportesTabLink.classList.add('border-green-600', 'text-green-600');
                reportesTabLink.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700');
            }
        }
    }


    // Inicializar el dashboard: cargar datos y configurar pestañas
    function initDashboard() {
        console.log('Iniciando dashboard de empresa...');
        loadEstadisticas(); // Cargar estadísticas
        loadComprasRecientes(); // Cargar compras recientes
        loadPreciosMercado(); // Cargar precios del mercado
        setupTabs(); // Configurar manejo de pestañas
    }

    // Llamar a la función de inicialización cuando el DOM esté completamente cargado
    initDashboard();

});

// Nota: Asegúrate de que las APIs backend (/empresa/estadisticas_compras, /empresa/compras, /empresa/precios_cafe)
// estén implementadas y retornen los datos en el formato esperado por este script.
// También verifica que el token JWT se guarde correctamente en localStorage o sessionStorage tras el login.
// Las URLs de las APIs (http://127.0.0.1:5000/...) deben coincidir con tu configuración. 