/* 
  Execute when the page finishes loading
  Gets the Django error elements and puts them inside a <div> (class="errorlist")
  Also makes the success <div> appears if theres any <ul> inside
*/
(function () {
    screen.orientation.lock("portrait");

    // Get the messages <ul>
    var messages = document.querySelector(".messages");

    // Get the errors <ul>
    var errorlists = document.querySelectorAll(".errorlist");

    if (messages != undefined) {
        // Insert every error <li> from each errorlist <ul> into the messages <ul>
        errorlists.forEach((errorlist) => {
            errors = errorlist.querySelectorAll("li");
            errors.forEach((error) => {
                error.classList.add("error");
                messages.insertAdjacentElement("afterbegin", error);
            });
        });

        messages.addEventListener("animationend", function () {
            setTimeout(function () {
                messages.remove();
            }, 0);
        });
    }
})();

function is_authenticated(is_authenticated, message) {
    if (!is_authenticated) alert(message);

    return is_authenticated;
}
