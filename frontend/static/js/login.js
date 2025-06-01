const API_BASE_URL = 'http://127.0.0.1:5000';

// Función genérica para manejar el inicio de sesión
async function handleLogin(event, userType) {
    event.preventDefault();
    
    const form = event.target;
    let identificador;
    // Obtener los elementos de mensaje directamente por ID
    let errorMessageDiv = document.getElementById('mensaje-error');
    let successMessageDiv = document.getElementById('mensaje-exito');

    // Limpiar mensajes anteriores
    errorMessageDiv.style.display = 'none';
    successMessageDiv.style.display = 'none';

    try {
        // Obtener el identificador según el tipo de usuario
        if (userType === 'campesino') {
            identificador = form.querySelector('input[name="cedula"]').value;
        } else if (userType === 'empresa') {
            identificador = form.querySelector('input[name="nit"]').value;
        } else if (userType === 'admin') {
            identificador = form.querySelector('input[name="identificador"]').value;
        }

        const password = form.querySelector('input[name="password"]').value;

        // Validación básica
        if (!identificador || !password) {
            throw new Error('Por favor complete todos los campos.');
        }

        // Preparar datos para el backend
        const loginData = {
            identificador: identificador,
            password: password,
            tipo_usuario: userType
        };

        // Intentar login en el backend API
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al iniciar sesión');
        }

        // Guardar token y datos del usuario en localStorage
        localStorage.setItem('access_token', data.token);
        localStorage.setItem('userType', data.tipo_usuario);
        localStorage.setItem('userData', JSON.stringify(data.usuario));

        // Enviar datos a la ruta /set_session en el frontend para establecer la sesión de Flask
        const setSessionResponse = await fetch(`/${data.tipo_usuario}/set_session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_type: data.tipo_usuario,
                user_data: data.usuario,
                token: data.token
            })
        });

        if (!setSessionResponse.ok) {
            throw new Error('Error al establecer la sesión en el frontend.');
        }

        // Mostrar mensaje de éxito
        successMessageDiv.textContent = '¡Inicio de sesión exitoso!';
        successMessageDiv.style.display = 'block';

        // Redireccionar al dashboard correspondiente
        setTimeout(() => {
            const dashboardUrl = `/${data.tipo_usuario}/dashboard`;
            window.location.href = dashboardUrl;
        }, 1000);

    } catch (error) {
        console.error('Error:', error);
        errorMessageDiv.textContent = error.message || 'Error de conexión con el servidor.';
        errorMessageDiv.style.display = 'block';
    }
}

// Añadir event listeners a los formularios específicos
document.addEventListener('DOMContentLoaded', () => {
    const campesinoLoginForm = document.getElementById('campesinoLoginForm');
    if (campesinoLoginForm) {
        campesinoLoginForm.addEventListener('submit', (e) => handleLogin(e, 'campesino'));
    }

    const empresaLoginForm = document.getElementById('empresaLoginForm');
    if (empresaLoginForm) {
        empresaLoginForm.addEventListener('submit', (e) => handleLogin(e, 'empresa'));
    }

    // Eliminar event listener para el formulario de administrador ya que la ruta del frontend lo maneja
    // const adminLoginForm = document.getElementById('adminLoginForm');
    // if (adminLoginForm) {
    //     adminLoginForm.addEventListener('submit', (e) => handleLogin(e, 'admin'));
    // }
});
