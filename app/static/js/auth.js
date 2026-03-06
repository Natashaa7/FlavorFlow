document.addEventListener("DOMContentLoaded", () => {

    window.showSignup = function () {
        document.getElementById("login").style.display = "none";
        document.getElementById("signup").style.display = "block";
    };
    window.showLogin = function () {
        document.getElementById("signup").style.display = "none";
        document.getElementById("login").style.display = "block";
    };

});
