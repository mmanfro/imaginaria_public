function check_email() {
    email = document.getElementById("email");
    email.focus();
    email = email.value;

    regex = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/;

    if (!regex.test(email)) alert("Insira um e-mail válido");

    return regex.test(email);
}
