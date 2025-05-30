// Variable global para almacenar los precios del café
let cafePrices = {};

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
                // Almacenar los precios en la variable global
                cafePrices = {
                    pergamino: parseFloat(data.precio_pergamino.replace(/[^0-9]/g, '')) || 0,
                    pasilla: parseFloat(data.precio_pasilla.replace(/[^0-9]/g, '')) || 0
                };
                console.log('Precios de café cargados:', cafePrices);

                // Actualizar los elementos en el HTML con los precios obtenidos
                const precioCafeCargaElement = document.getElementById('precio-cafe-carga');
                const precioPasillaElement = document.getElementById('precio-pasilla');
                const fechaPrecioCargaElement = document.getElementById('fecha-precio-carga');
                const fechaPrecioPasillaElement = document.getElementById('fecha-precio-pasilla');

                if (precioCafeCargaElement) {
                    precioCafeCargaElement.innerText = `$${cafePrices.pergamino.toLocaleString('es-CO')}`;
                }

                if (precioPasillaElement) {
                     precioPasillaElement.innerText = `$${cafePrices.pasilla.toLocaleString('es-CO')}`;
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
                // Puedes mostrar un mensaje de error en el UI si lo deseas
                const precioCafeCargaElement = document.getElementById('precio-cafe-carga');
                const precioPasillaElement = document.getElementById('precio-pasilla');
                if (precioCafeCargaElement) precioCafeCargaElement.innerText = 'Error';
                if (precioPasillaElement) precioPasillaElement.innerText = 'Error';
            });
    }

    fetchPreciosCafe();
});
