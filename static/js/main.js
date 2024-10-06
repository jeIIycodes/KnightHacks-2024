// static/js/main.js

function navigateTo(page) {
    window.location.href = `/${page}`;
}

function login() {
    window.location.href = '/api/auth/login';
}

function logout() {
    window.location.href = '/api/auth/logout';
}

// Optional: Additional client-side logic can be added here
