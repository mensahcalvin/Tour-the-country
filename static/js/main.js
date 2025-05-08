// Custom JavaScript for Explore Ghana

// Theme Management
const themeToggle = document.getElementById('themeToggle');
const themeIcon = themeToggle?.querySelector('i');

// Initialize theme from localStorage
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

// Update theme icon based on current theme
function updateThemeIcon(theme) {
    if (!themeIcon) return;
    themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
}

// Toggle theme
function toggleTheme() {
    if (!themeToggle) return;
    
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

// Dropdown Management
function initializeDropdowns() {
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    let isOpen = false;

    if (!dropdownToggle || !dropdownMenu) return;

    // Add animation classes
    dropdownMenu.classList.add('dropdown-animation');

    // Custom dropdown toggle
    dropdownToggle.addEventListener('click', function(e) {
        e.preventDefault();
        isOpen = !isOpen;
        
        if (isOpen) {
            dropdownMenu.style.display = 'block';
            dropdownMenu.style.opacity = '0';
            dropdownMenu.style.transform = 'translateY(-10px)';
            
            // Trigger animation
            setTimeout(() => {
                dropdownMenu.style.opacity = '1';
                dropdownMenu.style.transform = 'translateY(0)';
            }, 10);
        } else {
            dropdownMenu.style.opacity = '0';
            dropdownMenu.style.transform = 'translateY(-10px)';
            
            // Hide after animation
            setTimeout(() => {
                dropdownMenu.style.display = 'none';
            }, 300);
        }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
            isOpen = false;
            dropdownMenu.style.opacity = '0';
            dropdownMenu.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                dropdownMenu.style.display = 'none';
            }, 300);
        }
    });

    // Add hover effect for dropdown items
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Password strength checker
function checkPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[^a-zA-Z0-9]+/)) strength++;

    return strength;
}

// Image preview for file uploads
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (!preview) return;

    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll to top button
function initializeScrollToTop() {
    const scrollButton = document.getElementById('scrollToTop');
    if (!scrollButton) return;

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollButton.style.display = 'block';
        } else {
            scrollButton.style.display = 'none';
        }
    });
}

// Mobile menu toggle
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    if (!menu) return;

    menu.classList.toggle('show');
}

// Form submission handler
function handleFormSubmit(formId, successCallback, errorCallback) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm(formId)) {
            if (successCallback) successCallback();
        } else {
            if (errorCallback) errorCallback();
        }
    });
}

// Initialize map functionality
function initMap() {
    // This function is called by the Google Maps API
    // Implementation is in the map.html template
}

// Handle transportation type selection
function showTransportDetails(type) {
    const detailsDiv = document.getElementById('transportDetails');
    if (!detailsDiv) return;

    // Implementation is in the transportation.html template
}

// Handle itinerary creation
function createItinerary() {
    const form = document.querySelector('#itineraryForm');
    if (!form) return;

    const formData = new FormData(form);
    const itinerary = {
        name: formData.get('tripName'),
        startDate: formData.get('startDate'),
        endDate: formData.get('endDate'),
        destinations: Array.from(formData.getAll('destinations'))
    };

    // Here you would typically save the itinerary to the backend
    console.log('Creating itinerary:', itinerary);
}

// Initialize all functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initializeTheme();
    toggleTheme();

    // Initialize dropdowns
    initializeDropdowns();

    // Initialize scroll to top
    initializeScrollToTop();

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize form handlers
    handleFormSubmit('loginForm', 
        () => console.log('Login successful'),
        () => console.log('Login failed')
    );

    handleFormSubmit('registerForm',
        () => console.log('Registration successful'),
        () => console.log('Registration failed')
    );

    // Add scroll to top button to DOM
    const scrollButton = document.createElement('button');
    scrollButton.id = 'scrollToTop';
    scrollButton.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3';
    scrollButton.innerHTML = '↑';
    scrollButton.onclick = scrollToTop;
    document.body.appendChild(scrollButton);
}); 
