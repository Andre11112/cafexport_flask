document.addEventListener('DOMContentLoaded', function() {
    // Función para formatear números como moneda colombiana
    function formatearMoneda(valor) {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0
        }).format(valor);
    }

    // Función para formatear números como porcentaje
    function formatearPorcentaje(valor) {
        return new Intl.NumberFormat('es-CO', {
            style: 'percent',
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }).format(valor / 100);
    }

    // Función para cargar los reportes
    async function cargarReportes() {
        // Obtener el token de localStorage o sessionStorage, usando la clave 'access_token'
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

        // Verificar si el token existe
        if (!token) {
            console.error('Error: No se encontró token JWT en localStorage/sessionStorage.');
            alert('Por favor, inicie sesión para ver los reportes.');
            // Opcional: Redirigir a la página de login si no hay token
            // window.location.href = '/campesino/login';
            return; // Salir de la función si no hay token
        }

        try {
            // Realizar la solicitud a la API del backend
            const response = await fetch(`${API_BASE_URL}/campesino/reportes_campesino`, {
                method: 'GET', // Especificar el método HTTP
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json' // Incluir la cabecera Content-Type
                }
            });

            if (!response.ok) {
                throw new Error('Error al cargar los reportes');
            }

            const data = await response.json();

            // Actualizar las tarjetas de estadísticas
            document.querySelector('[data-stat="total_ventas"]').textContent = formatearMoneda(data.total_ventas);
            document.querySelector('[data-stat="cantidad_kg"]').textContent = `${data.cantidad_kg} kg`;
            document.querySelector('[data-stat="precio_promedio"]').textContent = formatearMoneda(data.precio_promedio);
            document.querySelector('[data-stat="mes_actual"]').textContent = formatearMoneda(data.mes_actual);
            document.querySelector('[data-stat="mes_diferencia"]').textContent = formatearPorcentaje(data.mes_diferencia);
            document.querySelector('[data-stat="anio_actual"]').textContent = formatearMoneda(data.anio_actual);
            document.querySelector('[data-stat="anio_diferencia"]').textContent = formatearPorcentaje(data.anio_diferencia);

            // Actualizar gráfico de ventas por mes
            const ventasPorMesCtx = document.getElementById('ventasPorMes').getContext('2d');
            new Chart(ventasPorMesCtx, {
                type: 'line',
                data: {
                    labels: data.ventas_por_mes.labels,
                    datasets: [{
                        label: 'Ventas por Mes',
                        data: data.ventas_por_mes.data,
                        borderColor: '#16a34a',
                        backgroundColor: 'rgba(22, 163, 74, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return formatearMoneda(value);
                                }
                            }
                        }
                    }
                }
            });

            // Actualizar gráfico de ventas por tipo
            const ventasPorTipoCtx = document.getElementById('distribucionCafe').getContext('2d');
            new Chart(ventasPorTipoCtx, {
                type: 'pie',
                data: {
                    labels: data.ventas_por_tipo.labels,
                    datasets: [{
                        data: data.ventas_por_tipo.data,
                        backgroundColor: ['#16a34a', '#86efac', '#dcfce7']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });

        } catch (error) {
            console.error('Error:', error);
            // Mostrar mensaje de error al usuario
            alert('Error al cargar los reportes. Por favor, intente nuevamente.');
        }
    }

    // Cargar reportes al iniciar
    cargarReportes();

    // Manejar cambio de período
    const selectPeriodo = document.querySelector('select');
    if (selectPeriodo) {
        selectPeriodo.addEventListener('change', cargarReportes);
    }

    // Manejar exportación
    const btnExportar = document.querySelector('button');
    if (btnExportar) {
        btnExportar.addEventListener('click', async function() {
            try {
                const response = await fetch('/api/campesino/exportar_reportes', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Error al exportar los reportes');
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'reportes_campesino.xlsx';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

            } catch (error) {
                console.error('Error:', error);
                alert('Error al exportar los reportes. Por favor, intente nuevamente.');
            }
        });
    }
});
