function toggleDarkMode() {
    document.body.classList.toggle("dark");

    const icon = document.getElementById("darkIcon");

    if (document.body.classList.contains("dark")) {
        icon.textContent = "dark_mode";
        localStorage.setItem("theme", "dark");
    } else {
        icon.textContent = "light_mode";
        localStorage.setItem("theme", "light");
    }
}

// Load theme when page opens
window.onload = function () {
    const savedTheme = localStorage.getItem("theme");
    const icon = document.getElementById("darkIcon");

    if (savedTheme === "dark") {
        document.body.classList.add("dark");
        if (icon) icon.textContent = "dark_mode";
    } else {
        document.body.classList.remove("dark");
        if (icon) icon.textContent = "light_mode";
    }
};
