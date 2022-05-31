(function () {
    screen.orientation.lock("portrait");
});

function is_authenticated(is_authenticated, message) {
    if (!is_authenticated) alert(message);

    return is_authenticated;
}
