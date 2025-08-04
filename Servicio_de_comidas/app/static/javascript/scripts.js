/* 
This is a SAMPLE FILE to get you started.
Please, follow the project instructions to complete the tasks.
*/
document.addEventListener('DOMContentLoaded', () => {
    const accessToken = localStorage.getItem('access_token');
    const loginLink = document.getElementById('login-link');
    const logoutButton = document.getElementById('logout-link');
    const placesListSection = document.getElementById('places-list');
    const url = 'http://localhost:5000/api/v1/places/';
    let listOfPlaces = [];

    const requestOptions = {  // creamos un header general
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };
    if (accessToken) {
        requestOptions.headers['Authorization'] = `Bearer ${accessToken}`; // Añadimos el token de acceso a las cabeceras
    }

    /*##########################################################
    -------------- LOGICA DE AUTENTICACION ---------------------
    ############################################################*/

    // #-#-# función para verificar la autenticación #-#-#

    async function checkAuthentication() { 
        if (accessToken) {
            if (loginLink) {
                loginLink.style.display = 'none'; // ocultamos el enlace de login si el usuario ya está autenticado
            }
            if (logoutButton) {
                logoutButton.style.display = 'block';
                logoutButton.onclick = () => { // detectamos el cierre de sesión
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('user_id');      // eliminamos el token de acceso y el id del almacenamiento local
                    window.location.reload();               // redirigimos al usuario a la página principal
                };
            }
            // Si el usuario está autenticado, renderizamos los lugares
            renderPlaces();
        } else {
            if (loginLink) {
                loginLink.style.display = 'block'; // mostramos el enlace de login si el usuario no está autenticado
            }
            if (logoutButton) {
                logoutButton.style.display = 'none'; // ocultamos el botón de logout si el usuario no está autenticado
            }
            // Si no hay token de acceso, mostramos un mensaje de iniciar sesion
            placesListSection.innerHTML = '<p class="error-message">Por favor, inicie sesión.</p>';
        }
    }

    /*#####################################################
    ----- LOGICA DE MOSTRAR PLACES DINAMICAMENTE ----------
    #######################################################*/

    // #-#-# Función para obtener los datos desde la API #-#-#
    
    async function fetchPlaces() {
        try {
            // URL para conectar con el endpoint de la API
            const response = await fetch(url, requestOptions);
            
            if (!response.ok) {
                // manejamos la no autorizacion del cliente
                if (response.status === 401) {
                    console.error('Unauthorized access - invalid token');
                    localStorage.removeItem('access_token'); // eliminamos el token de acceso
                    localStorage.removeItem('user_id');     // eliminamos el user_id
                    checkAuthentication();   // volvemos a verificar la autenticación
                    return [];
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data; // Devuelve los datos
        } catch (error) {
            console.error('Error fetching places:', error);
            // Mostramos un mensaje de error en la UI si la API falla
            placesListSection.innerHTML = '<p class="error-message">No se pudieron cargar los lugares. Por favor, inténtelo más tarde.</p>';
            return []; // Retorna un array vacío para evitar errores posteriores
        }
    }

    // #-#-# Función que obtiene todos los lugares y llama a filteredPlaces() #-#-#

    async function renderPlaces() {
        const places = await fetchPlaces();

        listOfPlaces = places;
        filteredPlaces(listOfPlaces) // Guardamos los datos obtenidos en la variable listOfPlaces
    }

    // #-#-# Función para renderizar los lugares filtrados #-#-#

    async function filteredPlaces(listOfPlaces) {
        
        const places = listOfPlaces; // Usamos la variable global listOfPlaces
        // Limpiar cualquier contenido existente
        placesListSection.innerHTML = '';

        // si la lista es igual a 0
        if (places.length === 0) {
            placesListSection.innerHTML = '<p class="no-places-found">No hay lugares disponibles en este momento.</p>';
            return;
        }

        places.forEach(place => {
            const article = document.createElement('article');
            article.classList.add('place-card'); // indicamos que articulo crear

            // Construye el HTML interno del article usando los datos del 'place'
            article.innerHTML = `
                <h2 class="place-card-title">${place.title}</h2>
                <h5 class="place-card-price">price per night: $${place.price}</h5>
                <a class="details-button" href="/places?id=${place.id}">View Details</a>
                <div class="place-details">
                </div>
            `;
            placesListSection.appendChild(article);
        });
    }

    // llamada principal para verificar la autenticación y renderizar los lugares 
    checkAuthentication();

    // #-#-# lógica para el filtrado de precios #-#-#-
    const priceFilter = document.getElementById('price-filter');
    priceFilter.addEventListener('change', (event) => {
        const filterValue = event.target.value;
        let placesToShow = [];
        console.log('Filtro de precio seleccionado:', filterValue);
        if (filterValue === 'all') { 
            placesToShow = listOfPlaces; // Si se selecciona "all", mostramos todos los lugares
            filteredPlaces(placesToShow);
        } else {
            if (filterValue === '10') {
                placesToShow = listOfPlaces.filter(place => place.price <= 10); // Filtramos precios menores o iguales a 10
            }
            else if (filterValue === '50') {
                placesToShow = listOfPlaces.filter(place => place.price <= 50); // Filtramos precios menores o iguales a 50
            }
            else if (filterValue === '100') {
                placesToShow = listOfPlaces.filter(place => place.price <= 100); // Filtramos precios menores o iguales a 100
            }
            filteredPlaces(placesToShow); // Llamamos a la función para renderizar los places
        }
    });
});