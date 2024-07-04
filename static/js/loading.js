// static/js/loading.js
document.addEventListener("DOMContentLoaded", function() {
    function showLoading() {
        const overlay = document.querySelector('.loading-overlay');
        overlay.style.display = 'flex';
    }

    function hideLoading() {
        const overlay = document.querySelector('.loading-overlay');
        overlay.style.display = 'none';
    }

    // Tornar as funções globalmente acessíveis
    window.showLoading = showLoading;
    window.hideLoading = hideLoading;
});
