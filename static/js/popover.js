// static/js/popover.js
document.addEventListener("DOMContentLoaded", function() {
    // Função para mostrar o popover com mensagem
    function showPopover(message) {
        // Criar o elemento popover
        const popover = document.createElement('div');
        popover.className = 'popover';
        popover.textContent = message;

        // Adicionar o popover ao corpo da página
        document.body.appendChild(popover);

        // Animação para deslizar de cima para baixo
        setTimeout(() => {
            popover.classList.add('show');
        }, 100);

        // Remover o popover após 2 segundos
        setTimeout(() => {
            popover.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(popover);
            }, 500);
        }, 2000);
    }

    // Tornar a função globalmente acessível
    window.showPopover = showPopover;
});
