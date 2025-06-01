document.addEventListener('DOMContentLoaded', () => {
    // Función para cargar las estadísticas del administrador
    async function loadAdminStats() {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/admin/stats`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const stats = await response.json();
            
            // Actualizar los elementos HTML con los datos recibidos
            document.getElementById('total-campesinos').textContent = stats.total_campesinos;
            document.getElementById('total-empresas').textContent = stats.total_empresas;
            // Actualizar volumen y valor total
            document.getElementById('volumen-total').textContent = `${stats.volumen_total_cafe} kg`;
            // Formatear valor total como moneda COP (ej: 82,010,000 COP)
            document.getElementById('valor-total').textContent = `${stats.valor_total_transacciones.toLocaleString('es-CO')} COP`;

        } catch (error) {
            console.error('Error loading admin stats:', error);
            // Opcional: Mostrar un mensaje de error en el dashboard
        }
    }

    // Función para cargar y mostrar la tabla de ventas de campesinos
    async function loadVentasTable() {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/admin/ventas`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const ventas = await response.json();

            const tbody = document.querySelector('#ventas-campesinos-section tbody');
            tbody.innerHTML = ''; // Limpiar la tabla actual

            if (ventas.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="px-6 py-4 text-center text-gray-500">No hay ventas registradas.</td></tr>';
                return;
            }

            ventas.forEach(venta => {
                // Extraer solo el valor del Enum (ej: 'Pasilla' de 'TipoCafeEnum.Pasilla')
                const tipoCafe = venta.tipo_cafe ? venta.tipo_cafe.split('.').pop() : 'N/A';
                const estadoVenta = venta.estado ? venta.estado.split('.').pop() : 'N/A';

                const row = `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            ${venta.fecha ? new Date(venta.fecha).toLocaleDateString() : 'N/A'}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            ${venta.campesino_nombre || 'N/A'}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getEstadoClass(estadoVenta)}">${tipoCafe}</span></td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${venta.cantidad !== undefined ? venta.cantidad + ' kg' : 'N/A'}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${venta.precio_kg !== undefined ? formatCOP(venta.precio_kg) + '/kg' : 'N/A'}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${venta.total !== undefined ? formatCOP(venta.total) : 'N/A'}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getEstadoClass(estadoVenta)}">${estadoVenta}</span></td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"><button class="btn-edit-estado text-green-600 hover:text-green-900" data-id="${venta.id}" data-tipo="venta" data-estado="${estadoVenta}">Edit</button></td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });

            agregarEventosEdit();

        } catch (error) {
            console.error('Error loading ventas table:', error);
            const tbody = document.querySelector('#ventas-campesinos-section tbody');
            if(tbody) tbody.innerHTML = '<tr><td colspan="8" class="px-6 py-4 text-center text-red-500">Error al cargar ventas.</td></tr>';
        }
    }

    // Función para cargar y mostrar la tabla de compras de empresas
    async function loadComprasTable() {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/admin/compras`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const compras = await response.json();

            const tbody = document.querySelector('#compras-empresas-section tbody');
            tbody.innerHTML = ''; // Limpiar la tabla actual

            if (compras.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="px-6 py-4 text-center text-gray-500">No hay compras registradas.</td></tr>';
                return;
            }

            compras.forEach(compra => {
                // Extraer solo el valor del Enum (ej: 'Arabica' de 'TipoCafeEnum.Arabica')
                 const tipoCafe = compra.tipo_cafe ? compra.tipo_cafe.split('.').pop() : 'N/A';
                 const estadoCompra = compra.estado ? compra.estado.split('.').pop() : 'N/A';

                const row = `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            ${compra.fecha_orden ? new Date(compra.fecha_orden).toLocaleDateString() : 'N/A'}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            ${compra.empresa_nombre || 'N/A'}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getEstadoClass(estadoCompra)}">${tipoCafe}</span></td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${compra.cantidad !== undefined ? compra.cantidad + ' kg' : 'N/A'}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${compra.precio_kg !== undefined ? formatCOP(compra.precio_kg) + '/kg' : 'N/A'}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${compra.total !== undefined ? formatCOP(compra.total) : 'N/A'}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getEstadoClass(estadoCompra)}">${estadoCompra}</span></td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"><button class="btn-edit-estado text-green-600 hover:text-green-900" data-id="${compra.id}" data-tipo="compra" data-estado="${estadoCompra}">Edit</button></td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });

            agregarEventosEdit();

        } catch (error) {
            console.error('Error loading compras table:', error);
            const tbody = document.querySelector('#compras-empresas-section tbody');
             if(tbody) tbody.innerHTML = '<tr><td colspan="8" class="px-6 py-4 text-center text-red-500">Error al cargar compras.</td></tr>';
        }
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

    // Función para formatear números como moneda COP
    const formatCOP = (amount) => {
        if (amount === undefined || amount === null) return 'N/A';
        return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(amount);
    };

    function agregarEventosEdit() {
        document.querySelectorAll('.btn-edit-estado').forEach(btn => {
            btn.onclick = function() {
                const id = this.dataset.id;
                const tipo = this.dataset.tipo;
                const estado = this.dataset.estado;
                abrirModalEstado(id, tipo, estado);
            }
        });
    }

    // Función para abrir el modal y cargar datos
    function abrirModalEstado(id, tipo, estadoActual) {
        document.getElementById('modal-item-id').value = id;
        document.getElementById('modal-item-tipo').value = tipo;
        document.getElementById('modal-estado-actual').textContent = estadoActual;
        document.getElementById('modal-nuevo-estado').value = estadoActual;
        document.getElementById('modal-cambiar-estado').classList.remove('hidden');
    }
    function cerrarModalEstado() {
        document.getElementById('modal-cambiar-estado').classList.add('hidden');
    }

    // Enviar el cambio de estado
    const form = document.getElementById('form-cambiar-estado');
    if(form) {
        form.onsubmit = async function(e) {
            e.preventDefault();
            const id = document.getElementById('modal-item-id').value;
            const tipo = document.getElementById('modal-item-tipo').value;
            const nuevoEstado = document.getElementById('modal-nuevo-estado').value;
            let url = '';
            if(tipo === 'venta') {
                url = `/admin/ventas/${id}/estado`;
            } else {
                url = `/admin/compras/${id}/estado`;
            }
            const resp = await fetch(url, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ estado: nuevoEstado })
            });
            if(resp.ok) {
                cerrarModalEstado();
                if(typeof loadVentasTable === 'function') loadVentasTable();
                if(typeof loadComprasTable === 'function') loadComprasTable();
            } else {
                alert('Error al actualizar el estado');
            }
        }
    }

    // Llamar a las funciones para cargar datos cuando la página se cargue
    loadAdminStats();
    loadVentasTable();
    loadComprasTable();
}); 