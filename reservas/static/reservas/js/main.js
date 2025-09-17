// Funciones principales
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Validación de fechas en formularios
    setupDateValidation();
    
    // Animaciones
    setupScrollAnimations();
    
    // Búsqueda en tiempo real
    setupLiveSearch();
});

// Validación de fechas
function setupDateValidation() {
    const checkInInput = document.getElementById('id_check_in');
    const checkOutInput = document.getElementById('id_check_out');
    
    if (checkInInput && checkOutInput) {
        checkInInput.addEventListener('change', function() {
            const checkInDate = new Date(this.value);
            const minCheckOut = new Date(checkInDate);
            minCheckOut.setDate(minCheckOut.getDate() + 1);
            
            checkOutInput.min = minCheckOut.toISOString().split('T')[0];
            
            if (checkOutInput.value && new Date(checkOutInput.value) <= checkInDate) {
                checkOutInput.value = minCheckOut.toISOString().split('T')[0];
            }
        });
    }
}

// Animaciones al hacer scroll
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observar elementos con clase 'animate-on-scroll'
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Búsqueda en tiempo real para actividades
function setupLiveSearch() {
    const searchInput = document.getElementById('activity-search');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                const searchTerm = this.value.toLowerCase();
                const activityCards = document.querySelectorAll('.activity-card');
                
                activityCards.forEach(card => {
                    const title = card.querySelector('.card-title').textContent.toLowerCase();
                    const description = card.querySelector('.card-text').textContent.toLowerCase();
                    
                    if (title.includes(searchTerm) || description.includes(searchTerm)) {
                        card.closest('.col').style.display = 'block';
                    } else {
                        card.closest('.col').style.display = 'none';
                    }
                });
            }, 300);
        });
    }
}

// Función para mostrar loading spinner
function showLoading(element) {
    element.innerHTML = '<div class="spinner"></div>';
}

// Función para confirmar cancelación
function confirmCancel(message) {
    return confirm(message || '¿Estás seguro de que deseas cancelar?');
}

// Función para formatear precio
function formatPrice(price) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}

// Función para calcular noches y precio total
function calculateStayTotal() {
    const checkIn = document.getElementById('id_check_in');
    const checkOut = document.getElementById('id_check_out');
    const pricePerNight = parseFloat(document.querySelector('[data-price]')?.dataset.price || 0);
    const totalDisplay = document.getElementById('total-price');
    
    if (checkIn && checkOut && checkIn.value && checkOut.value && totalDisplay) {
        const startDate = new Date(checkIn.value);
        const endDate = new Date(checkOut.value);
        const nights = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
        
        if (nights > 0) {
            const total = nights * pricePerNight;
            totalDisplay.innerHTML = `
                <strong>${nights} noche${nights > 1 ? 's' : ''}</strong><br>
                <span class="price-display">${formatPrice(total)}</span>
            `;
        }
    }
}

// Event listeners para cálculo de precios
document.addEventListener('change', function(e) {
    if (e.target.id === 'id_check_in' || e.target.id === 'id_check_out') {
        calculateStayTotal();
    }
});