function toggle_contests(event, id) {
    headers = Array.from(document.getElementById("contest-headers").children);
    headers.forEach((element) => {
        element.classList.remove("active");
    });
    event.target.classList.add("active");

    contests = Array.from(document.getElementById("contests-wrapper").children);
    contests.forEach((element) => {
        element.classList.add("hidden");
    });
    document.getElementById(id).classList.remove("hidden");
}
