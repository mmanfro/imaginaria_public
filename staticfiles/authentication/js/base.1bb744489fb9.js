/* 
  Execute when the page finishes loading
  Gets the Django error elements and puts them inside a <div> (class="errorlist")
  Also makes the success <div> appears if theres any <ul> inside
*/
(function () {
  // Get the messages <ul>
  var messages = document.querySelector(".messages");

  // Get the errors <ul>
  var errorlists = document.querySelectorAll(".errorlist");

  // Insert every error <li> from each errorlist <ul> into the messages <ul>
  errorlists.forEach((errorlist) => {
    errors = errorlist.querySelectorAll("li");
    errors.forEach((error) => {
      error.classList.add("error");
      messages.insertAdjacentElement("afterbegin", error);
    });
  });
})();

function play() {
  var audio;

  switch (Math.floor(Math.random() * 4)) {
    case 0:
      audio = document.getElementById("woof-audio");
    case 1:
      audio = document.getElementById("doublewoof-audio");
      break;
    case 2:
      audio = document.getElementById("howl-audio");
      break;
    case 3:
      audio = document.getElementById("whine-audio");
      break;
    default:
      audio = document.getElementById("woof-audio");
  }

  audio.play();
}
