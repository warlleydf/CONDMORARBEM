// Função de validação do formulário
function validateForm() {
    const telefoneField = document.querySelector('input[name="telefone"]');
    const emailField = document.querySelector('input[name="email"]');

    // Validar campo de telefone
    const telefonePattern = /^\d*$/;
    if (!telefonePattern.test(telefoneField.value)) {
        alert('Por favor, insira apenas números no campo de telefone.');
        return false;
    }

    // Validar campo de email
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if (!emailPattern.test(emailField.value)) {
        alert('Por favor, insira um endereço de e-mail válido.');
        return false;
    }

    return true;  // Se todas as validações passarem
}