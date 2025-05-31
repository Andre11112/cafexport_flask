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

    // Cargar reportes al iniciar
    loadReportes();
});
