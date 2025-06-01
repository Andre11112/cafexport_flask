document.addEventListener('DOMContentLoaded', function() {
    // Función para formatear números como moneda COP
    const formatCOP = (amount) => {
        if (amount === null || amount === undefined) return '--';
        const numberAmount = parseFloat(amount);
        if (isNaN(numberAmount)) return '--';
        return `$${numberAmount.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
    };

    // Función para formatear números con decimales
    const formatNumber = (amount, decimals = 0) => {
        if (amount === null || amount === undefined) return '--';
        const numberAmount = parseFloat(amount);
        if (isNaN(numberAmount)) return '--';
        return numberAmount.toLocaleString('es-CO', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    };

    // Función para cargar los reportes
    function loadReportes() {
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
        
        fetch('http://127.0.0.1:5000/empresa/reportes_empresa', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Actualizar estadísticas
            document.querySelector('.total-compras-value').textContent = formatCOP(data.estadisticas.total_compras);
            document.querySelector('.total-compras-cantidad').textContent = `${formatNumber(data.estadisticas.total_cantidad, 2)} kg`;
            document.querySelector('.precio-promedio').textContent = `${formatCOP(data.estadisticas.precio_promedio)}/kg`;
            document.querySelector('.compras-ultimo-mes').textContent = formatCOP(data.estadisticas.compras_ultimo_mes);
            document.querySelector('.variacion-porcentual').textContent = 
                `${data.estadisticas.variacion_porcentual > 0 ? '+' : ''}${formatNumber(data.estadisticas.variacion_porcentual, 2)}%`;

            // Actualizar gráficos
            updateComprasPorMesChart(data.compras_por_mes);
            updateComprasPorTipoChart(data.compras_por_tipo);
            updateEvolucionPreciosCompraChart(data.precio_promedio_por_mes);

            // Poblar historial de compras
            populateHistorialComprasTable(data.historial_compras);
        })
        .catch(error => {
            console.error('Error:', error);
            // Mostrar mensaje de error en la interfaz
            const errorMessage = document.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.textContent = `Error al cargar reportes: ${error.message}`;
            }
        });
    }

    // Función para actualizar el gráfico de compras por mes
    function updateComprasPorMesChart(data) {
        const ctx = document.getElementById('comprasPorMesChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.mes),
                datasets: [{
                    label: 'Total Compras',
                    data: data.map(item => item.total),
                    borderColor: 'rgb(34, 197, 94)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // Función para actualizar el gráfico de compras por tipo
    function updateComprasPorTipoChart(data) {
        const ctx = document.getElementById('comprasPorTipoChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.map(item => item.tipo),
                datasets: [{
                    data: data.map(item => item.valor),
                    backgroundColor: [
                        'rgb(34, 197, 94)',
                        'rgb(234, 179, 8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // Función para actualizar el gráfico de evolución de precios de compra
    function updateEvolucionPreciosCompraChart(data) {
        const ctx = document.getElementById('evolucionPreciosCompraChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.mes),
                datasets: [{
                    label: 'Precio Promedio (COP/kg)',
                    data: data.map(item => item.precio_promedio),
                    borderColor: 'rgb(234, 179, 8)', // Color amarillo/naranja
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                 scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCOP(value); // Usar la función de formato para el eje Y
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Precio Promedio: ${formatCOP(context.raw)}/kg`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Función para poblar la tabla del historial de compras
    function populateHistorialComprasTable(compras) {
        const container = document.getElementById('historialComprasTableContainer');
        if (!container) {
            console.error('Contenedor de historial de compras no encontrado!');
            return;
        }

        // Limpiar contenido actual
        container.innerHTML = '';

        if (!compras || compras.length === 0) {
            container.innerHTML = '<p class="text-gray-500">No hay historial de compras disponible.</p>';
            return;
        }

        // Crear estructura de tabla
        let tableHTML = `
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha Orden</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo Café</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cantidad (kg)</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio/kg (COP)</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total (COP)</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notas</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendedor</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
        `;

        // Llenar tabla con datos
        compras.forEach(compra => {
            tableHTML += `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${compra.fecha_orden ? new Date(compra.fecha_orden).toLocaleDateString('es-CO') : 'N/A'}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            ${compra.tipo_cafe || 'N/A'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">${compra.cantidad !== null ? formatNumber(compra.cantidad, 2) : 'N/A'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">${compra.precio_kg !== null ? formatCOP(compra.precio_kg) : 'N/A'}/kg</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">${compra.total !== null ? formatCOP(compra.total) : 'N/A'}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                         <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${compra.estado === 'Completada' ? 'bg-green-100 text-green-800' : compra.estado === 'Pendiente' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'}">
                            ${compra.estado || 'N/A'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${compra.notas || 'N/A'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${compra.vendedor || 'N/A'}</td>
                </tr>
            `;
        });

        tableHTML += `
                </tbody>
            </table>
        `;

        container.innerHTML = tableHTML;
    }

    // Cargar reportes al iniciar
    loadReportes();
});
