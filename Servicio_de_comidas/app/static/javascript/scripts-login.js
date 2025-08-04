/*##############################################################
------------    LOGIN, REGISTRO ANIMADO      ------------------- 
################################################################*/

document.addEventListener("DOMContentLoaded", function() {
    // obtenemos los componentes
    const activadorCheckbox = document.getElementById("activador");
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");

    function changeVisibility(){
        // agrega un bloque de css a las forms dependiendo del checkbox
        // esto genera el intercambio de formularios
        if (activadorCheckbox.checked){
            registerForm.classList.add('form-active');
            loginForm.classList.remove('form-active');
        } else {
            registerForm.classList.remove('form-active');
            loginForm.classList.add('form-active');
        }
    }
    activadorCheckbox.checked = false;
    changeVisibility();

    activadorCheckbox.addEventListener('change', changeVisibility);

});
/* ########################################################
---------------- FUNCION LOGIN ---------------------------
######################################################### */
async function loginUser(email, password) {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
                method: 'POST', // ¡Siempre POST para login!
                headers: {
                    'Content-Type': 'application/json' // Indicamos que enviamos JSON
                },
                body: JSON.stringify({ // Convertimos los datos a JSON string
                    email: email,
                    password: password
                })
            });
            const data = await response.json(); // Parseamos la respuesta JSON del servidor

            if (response.ok) { // Si la respuesta HTTP es 2xx (ej. 200 OK)
                console.log('Login exitoso:', data);
                // Guarda el token de acceso y el user_id
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user_id', data.user_id);

                alert('¡Login exitoso! Redirigiendo...');

                // Redirige a la página principal después del login exitoso
                window.location.href = '/';
            } else {
                // Si la respuesta HTTP es un error 
                console.error('Error en el login:', data.error);
                alert(data.error || 'Error desconocido en el login.');
            }
        } catch (error) {
            // Esto captura errores de red
            console.error('Error de red o del servidor:', error);
            alert('No se pudo conectar con el servidor. Verifica tu conexión o la URL de la API.');
        }
}
/*
########################################################
-------------- CONEXION CON LA API ---------------------
----------------------- LOGIN --------------------------
#######################################################*/
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const loginEmailInput = document.getElementById('email-login');
    const loginPasswordInput = document.getElementById('password-login');

    // --- EVENT LISTENER PARA EL FORMULARIO DE LOGIN ---
    if (loginForm && loginEmailInput && loginPasswordInput) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Evita que la página se recargue al enviar el formulario

            const email = loginEmailInput.value;
            const password = loginPasswordInput.value;

            await loginUser(email, password); // funcion login
        });
    } else {
        console.error('Elementos del formulario de login no encontrados.');
    }
});
/*#######################################################
------------------ REGISTRO -----------------------------
#########################################################*/
document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const registerFirstName = document.getElementById('First_name');
    const registerLastName = document.getElementById('Last_name');
    const registerEmail = document.getElementById('email');
    const registerPassword = document.getElementById('password');

    // --- EVENT LISTENER PARA EL FORMULARIO DE REGISTRO ---
    registerForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Evita que la página se recargue al enviar el formulario

        const firstName = registerFirstName.value;
        const lastName = registerLastName.value;
        const email = registerEmail.value;
        const password = registerPassword.value;

        try {
            const response = await fetch('http://127.0.0.1:5000/api/v1/users', {
                method: 'POST', // para enviar los datos
                headers: {
                    'Content-Type': 'application/json' // para enviarlos en JSON
                },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    email: email,
                    password: password
                })
            });
            const data = await response.json(); //se parsea la respuesta json del server
            if (response.ok){
                console.log('registro exitoso:', data);
                alert('¡Registro exitoso! Ahora puedes iniciar sesión.');
                // se redirige al usuario al index.html
                window.location.href = '/';
            }
            else {
                console.error('Error en el registro:', data.error);
                alert(data.error || 'Error desconocido en el registro.');
            }
        } catch (error) {
            // Captura errores de red
            console.error('Error de red o del servidor:', error);
            alert('No se pudo conectar con el servidor. Verifica tu conexión o la URL de la API.');
        }
    });
});
