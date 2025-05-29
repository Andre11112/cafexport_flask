document.addEventListener('DOMContentLoaded', function() {
    // Función para obtener y mostrar los precios del café
    function fetchPreciosCafe() {
        fetch('http://127.0.0.1:5000/api/precios_cafe')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al obtener precios del café');
                }
                return response.json();
            })
            .then(data => {
                // Actualizar los elementos en el HTML con los precios obtenidos
                const precioCafeCargaElement = document.getElementById('precio-cafe-carga');
                const precioPasillaElement = document.getElementById('precio-pasilla');
                const fechaPrecioCargaElement = document.getElementById('fecha-precio-carga');
                const fechaPrecioPasillaElement = document.getElementById('fecha-precio-pasilla');

                if (precioCafeCargaElement) {
                    // Eliminar caracteres no numéricos (como puntos y $) y convertir a número para formatear
                    const precioCarga = parseFloat(data.precio_pergamino.replace(/[^0-9]/g, ''));
                    precioCafeCargaElement.innerText = `$${precioCarga.toLocaleString('es-CO')}`;
                }

                if (precioPasillaElement) {
                    // Eliminar caracteres no numéricos (como puntos y $) y convertir a número para formatear
                    const precioPasilla = parseFloat(data.precio_pasilla.replace(/[^0-9]/g, ''));
                    precioPasillaElement.innerText = `$${precioPasilla.toLocaleString('es-CO')}`;
                }

                // Actualizar fechas
                if (fechaPrecioCargaElement) {
                    fechaPrecioCargaElement.innerText = `Actualizado al ${new Date(data.fecha_actualizacion).toLocaleDateString()}`;
                }

                if (fechaPrecioPasillaElement) {
                    fechaPrecioPasillaElement.innerText = `Actualizado al ${new Date(data.fecha_actualizacion).toLocaleDateString()}`;
                }
            })
            .catch(error => {
                console.error('Error al obtener precios del café:', error);
            });
    }

    fetchPreciosCafe();
});
