// frontend/static/js/registro.js

// Función genérica para manejar el envío del formulario de registro
async function handleRegistrationSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const userType = form.id === 'registroCampesinoForm' ? 'campesino' : 'empresa';

    const data = {
        tipo_usuario: userType,
        nombre: formData.get('nombre'),
        email: formData.get('email'),
        password: formData.get('password'),
    };

    // Añadir campos específicos según el tipo de usuario
    if (userType === 'campesino') {
        data.cedula = formData.get('cedula');
        data.direccion_finca = formData.get('direccion_finca');
        // data.telefono = formData.get('telefono'); // Eliminar si no se usa/necesita
    } else if (userType === 'empresa') {
        data.nit = formData.get('nit');
        data.direccion_empresa = formData.get('direccion_empresa');
        // data.telefono = formData.get('telefono'); // Eliminar si no se usa/necesita
    }

    // Validaciones básicas
    let isValid = true;
    let errorMessage = '';

    if (!data.nombre || !data.password) {
        isValid = false;
        errorMessage = 'Nombre y contraseña son obligatorios.';
    }

    if (userType === 'campesino') {
        if (!data.cedula || !data.direccion_finca) {
            isValid = false;
            errorMessage = 'Cédula y dirección de finca son obligatorios para campesinos.';
        }
    } else if (userType === 'empresa') {
        if (!data.nit || !data.direccion_empresa) {
            isValid = false;
            errorMessage = 'NIT y dirección de empresa son obligatorios para empresas.';
        }
    }

    // Si hay un elemento para mensajes de error en el HTML, usarlo
    const errorElement = form.querySelector('#mensaje-error');
    const successElement = form.querySelector('#mensaje-exito');

    if (!isValid) {
        if (errorElement) {
            errorElement.textContent = errorMessage;
            errorElement.classList.remove('hidden');
            if (successElement) successElement.classList.add('hidden');
        } else {
             alert(errorMessage); // Fallback a alert si no hay elemento en HTML
        }
        return;
    } else {
         if (errorElement) errorElement.classList.add('hidden');
    }


    try {
        // Asegurarse de que la URL apunta al backend API
        const response = await fetch('http://127.0.0.1:5000/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }, // <-- Coma correcta aquí
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            const successMessage = result.mensaje || `${userType.capitalize()} registrado exitosamente`;
            if (successElement) {
                successElement.textContent = successMessage;
                successElement.classList.remove('hidden');
                if (errorElement) errorElement.classList.add('hidden');
            } else {
                alert(successMessage);
            }

            // Redirigir al login específico después de un registro exitoso
            // Obtener la URL de redirección del atributo data del formulario
            const redirectUrl = form.dataset.loginRedirectUrl;
            if (redirectUrl) {
                 setTimeout(() => {
                    window.location.href = redirectUrl; // <-- Punto y coma correcto aquí
                }, 2000);
            }


        } else {
            const errorMessage = result.error || `Error en el registro de ${userType}`;
             if (errorElement) {
                errorElement.textContent = errorMessage;
                errorElement.classList.remove('hidden');
                if (successElement) successElement.classList.add('hidden');
            } else {
                alert(errorMessage);
            }
        }
    } catch (error) {
        console.error('Error:', error);
        const connectionError = 'Error de conexión con el servidor backend';
         if (errorElement) {
            errorElement.textContent = connectionError;
            errorElement.classList.remove('hidden');
            if (successElement) successElement.classList.add('hidden');
        } else {
            alert(connectionError);
        }
    }
}

// Añadir event listeners a ambos formularios
const campesinoForm = document.getElementById('registroCampesinoForm');
if (campesinoForm) {
    campesinoForm.addEventListener('submit', handleRegistrationSubmit);
}

const empresaForm = document.getElementById('registroForm'); // Asumiendo 'registroForm' es el ID del formulario de empresa
if (empresaForm) {
    empresaForm.addEventListener('submit', handleRegistrationSubmit);
}
