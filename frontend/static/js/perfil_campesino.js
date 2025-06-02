document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM completamente cargado.'); // Log para verificar DOMContentLoaded
    const profileDisplay = document.getElementById('profile-display');
    const profileEditForm = document.getElementById('profile-edit-form');
    const editProfileBtn = document.getElementById('edit-profile-btn');
    const cancelEditBtn = document.getElementById('cancel-edit-btn');
    const updateProfileForm = document.getElementById('update-profile-form');

    const facturasTab = document.getElementById('facturas-tab');
    const produccionTab = document.getElementById('produccion-tab');
    const facturasContent = document.getElementById('facturas-content');
    const produccionContent = document.getElementById('produccion-content');

    // Función para mostrar una pestaña y ocultar la otra
    function showTab(tabToShow) {
        if (tabToShow === 'facturas') {
            facturasContent.classList.remove('hidden');
            produccionContent.classList.add('hidden');
            facturasTab.classList.add('border-green-500', 'text-green-600');
            facturasTab.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
            produccionTab.classList.remove('border-green-500', 'text-green-600');
            produccionTab.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
        } else if (tabToShow === 'produccion') {
            produccionContent.classList.remove('hidden');
            facturasContent.classList.add('hidden');
            produccionTab.classList.add('border-green-500', 'text-green-600');
            produccionTab.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
            facturasTab.classList.remove('border-green-500', 'text-green-600');
            facturasTab.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
        }
    }

    // Mostrar la pestaña de facturas disponibles por defecto
    showTab('facturas');

    // Event listeners para las pestañas
    facturasTab.addEventListener('click', (e) => {
        e.preventDefault();
        showTab('facturas');
    });

    produccionTab.addEventListener('click', (e) => {
        e.preventDefault();
        showTab('produccion');
    });

    // Lógica para mostrar/ocultar el formulario de edición del perfil
    editProfileBtn.addEventListener('click', () => {
        profileDisplay.classList.add('hidden');
        profileEditForm.classList.remove('hidden');
    });

    cancelEditBtn.addEventListener('click', () => {
        profileEditForm.classList.add('hidden');
        profileDisplay.classList.remove('hidden');
    });

    // Lógica para manejar el envío del formulario de actualización del perfil
    updateProfileForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(updateProfileForm);
        const data = Object.fromEntries(formData.entries());

        // Aquí puedes añadir el token de autorización si lo tienes almacenado en el frontend (ej: en localStorage)
        const token = localStorage.getItem('token'); // Asumiendo que el token se guarda en localStorage

        try {
            const response = await fetch('/api/profile/update', { // Esta URL deberá coincidir con la ruta en Flask
                method: 'PUT', // O POST, dependiendo de cómo implementes el backend
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // Incluir el token de autorización
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                // Opcional: actualizar la vista con los nuevos datos o recargar la página
                window.location.reload();
            } else {
                alert(`Error: ${result.error || result.message || 'Error desconocido'}`);
            }
        } catch (error) {
            console.error('Error al actualizar el perfil:', error);
            alert('Ocurrió un error al actualizar el perfil.');
        }
    });

    // ** Nueva lógica para cargar y mostrar facturas completadas **

    // Función para obtener y mostrar las facturas completadas
    async function fetchAndDisplayFacturasCompletadas() {
        console.log('fetchAndDisplayFacturasCompletadas llamada'); // Log inicio función
        const jwtToken = localStorage.getItem('token'); // Obtener el token JWT (usando 'token' como en el script original)

        console.log('Token JWT obtenido:', jwtToken); // Log del token

        if (!jwtToken) {
            console.error('No JWT token found. User not authenticated?');
            // Redirigir a la página de login si no hay token
            // alert('Tu sesión ha expirado o no has iniciado sesión. Por favor, inicia sesión de nuevo.');
            // window.location.href = '/campesino/login'; // Ajusta esta URL si es diferente
            return; // Salir si no hay token (asumimos que la ruta ya protege el acceso)
        }

        try {
            // Llamar al endpoint del perfil que devuelve las facturas completadas
            const response = await fetch('/api/campesino/perfil', { 
                method: 'GET',
                headers: {
                    'Authorization': 'Bearer ' + jwtToken // Incluir el token JWT
                }
            });

            if (!response.ok) {
                 const errorData = await response.json();
                 throw new Error(errorData.error || 'Error al obtener facturas completadas');
            }

            const data = await response.json();
            const facturasCompletadas = data.facturas_completadas || [];

            console.log('Facturas completadas recibidas:', facturasCompletadas);

            populateFacturasTable(facturasCompletadas); // Llenar la tabla con los datos

        } catch (error) {
            console.error('Error fetching completed invoices:', error);
            // Mostrar mensaje de error en la tabla
            const tbody = document.querySelector('#facturas-content table tbody');
            if (tbody) {
                tbody.innerHTML = `<tr><td colspan="4" class="px-6 py-4 text-center text-red-500">Error al cargar facturas: ${error.message}</td></tr>`;
            }
        }
    }

    // Función para poblar la tabla de facturas completadas
    function populateFacturasTable(facturas) {
        console.log('populateFacturasTable llamada con facturas:', facturas); // Log datos recibidos
        const tbody = document.querySelector('#facturas-content table tbody');
        if (!tbody) {
            console.error('Table body for invoices not found!'); // Log si no encuentra tbody
            return;
        }

        tbody.innerHTML = ''; // Limpiar contenido actual de la tabla

        const noFacturasMessage = document.querySelector('#facturas-content > p');
        if (noFacturasMessage) noFacturasMessage.classList.add('hidden'); // Ocultar el mensaje por defecto

        if (!facturas || facturas.length === 0) {
            // Mostrar mensaje si no hay facturas
            if (noFacturasMessage) noFacturasMessage.classList.remove('hidden');
            tbody.innerHTML = ''; // Asegurarse de que la tabla esté vacía
            return;
        }

        facturas.forEach(factura => {
            // Formatear la fecha (asumiendo que factura.fecha ya viene formateada o es un string parseable)
            const fechaFactura = factura.fecha ? new Date(factura.fecha).toLocaleDateString('es-CO') : 'N/A';

            // Formatear cantidad, precio y total con separadores de miles y símbolo COP
            // Nota: Los datos vienen como números o strings de números, parseFloat y toLocaleString son útiles
            const cantidadFormateada = factura.cantidad ? parseFloat(factura.cantidad).toLocaleString('es-CO', { maximumFractionDigits: 2 }) : '0';
            const totalFormateado = factura.total ? parseFloat(factura.total).toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) : '0'; // Formateado a COP sin decimales como en HTML

            const row = `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${fechaFactura}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${cantidadFormateada} kg
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        $ ${totalFormateado} COP
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <a href="#" class="text-green-600 hover:text-green-900 download-factura-perfil-btn" data-venta-id="${factura.id}">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l3-3m-3 3l-3-3m2-8H7a2 2 0 00-2 2v10a2 2 0 002 2h7v-2m2-4h2a2 2 0 002-2V6a2 2 0 00-2-2h-2m-4-2v2m0 8H9"></path></svg>
                        </a>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });

         // Añadir event listener a los botones de descarga DESPUÉS de poblar la tabla
        addDownloadListeners();
    }

    // Función para descargar la factura (adaptada de ventas_campesino.js)
    async function downloadFactura(ventaId) {
        const jwtToken = localStorage.getItem('token'); // Usar 'token'

        if (!jwtToken) {
            console.error('No JWT token found for factura download.');
            alert('Por favor, inicie sesión para descargar la factura.');
            window.location.href = '/campesino/login';
            return;
        }

        try {
            // Usar la URL correcta del backend para la descarga de factura
            const response = await fetch(`/api/ventas/${ventaId}/factura`, {
                method: 'GET',
                headers: {
                    'Authorization': 'Bearer ' + jwtToken
                    // 'Content-Type': 'application/json' // No siempre necesario para descarga de archivos
                }
            });

            if (!response.ok) {
                 // Intentar leer el cuerpo del error si es JSON, de lo contrario mostrar status
                 try {
                     const errorData = await response.json();
                     throw new Error(errorData.error || 'Error desconocido al descargar la factura');
                 } catch (e) {
                     throw new Error(`Error de red o servidor (${response.status}) al descargar la factura.`);
                 }
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

    // Función para añadir event listeners a los botones de descarga
    function addDownloadListeners() {
        const ventasTableBody = document.querySelector('#facturas-content table tbody');
        if (ventasTableBody) {
            ventasTableBody.addEventListener('click', function(event) {
                const target = event.target;
                // Verificar si se hizo clic en el ícono o el enlace de descarga con la clase específica
                const downloadLink = target.closest('.download-factura-perfil-btn');
                if (downloadLink) {
                    event.preventDefault(); // Prevenir el comportamiento por defecto del enlace
                    const ventaId = downloadLink.getAttribute('data-venta-id');
                    if (ventaId) {
                        downloadFactura(ventaId);
                    }
                }
            });
        }
    }

    // Llamar a la función para cargar y mostrar facturas al cargar el DOM
    fetchAndDisplayFacturasCompletadas();
});
