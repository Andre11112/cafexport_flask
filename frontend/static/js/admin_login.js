document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('adminLoginForm');
    const mensajeError = document.getElementById('mensaje-error');
    const mensajeExito = document.getElementById('mensaje-exito');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevenir el envío del formulario tradicional

            mensajeError.style.display = 'none';
            mensajeExito.style.display = 'none';

            const identificador = document.getElementById('email').value; // El input tiene ID 'email'
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/auth/login', { // Usar la ruta API del backend
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        identificador: identificador,
                        password: password,
                        tipo_usuario: 'admin' // Especificar el tipo de usuario
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Login exitoso
                    localStorage.setItem('token', data.token); // Guardar el token en localStorage
                    localStorage.setItem('user', JSON.stringify(data.usuario)); // Opcional: guardar datos del usuario
                    
                    mensajeExito.textContent = data.mensaje || 'Inicio de sesión exitoso';
                    mensajeExito.style.display = 'block';

                    // Redirigir al dashboard después de un breve retraso
                    setTimeout(() => {
                        window.location.href = '/admin/dashboard';
                    }, 1000);

                } else {
                    // Error en el login
                    mensajeError.textContent = data.error || 'Error en el inicio de sesión';
                    mensajeError.style.display = 'block';
                }
            } catch (error) {
                console.error('Error de red o solicitud:', error);
                mensajeError.textContent = 'Error de conexión. Intente de nuevo.';
                mensajeError.style.display = 'block';
            }
        });
    }
});

// Función para mostrar mensajes (si es necesario en el futuro)
/*
function mostrarMensaje(tipo, mensaje) {
    const targetElement = tipo === 'success' ? mensajeExito : mensajeError;
    if (targetElement) {
        targetElement.textContent = mensaje;
        targetElement.style.display = 'block';
        // Opcional: ocultar después de un tiempo
        // setTimeout(() => { targetElement.style.display = 'none'; }, 5000);
    }
}
*/ 