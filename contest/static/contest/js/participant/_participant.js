function vote(id, n = 0) {
    for (let index = 1; index <= 5; index++) {
        rating = document.getElementById("vote_" + id + "_" + index);
        if (index <= n) {
            rating.src =
                static_url + "imaginaria/images/LovelyHouse_filled.png";
        } else {
            rating.src = static_url + "imaginaria/images/LovelyHouse_empty.png";
        }
    }
}
