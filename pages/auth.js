document.addEventListener("DOMContentLoaded", () => {
    // Toggle between signup and login
    window.showSignup = function () {
        document.getElementById("auth").classList.add("signup-mode");
    };

    window.showLogin = function () {
        document.getElementById("auth").classList.remove("signup-mode");
    };
    // Fetch users from FastAPI
    fetch("http://localhost:8000/users")
        .then(response => response.json())
        .then(users => {
            const list = document.getElementById("user-list");
            users.forEach(user => {
                const li = document.createElement("li");
                li.textContent = `${user.email} - ${user.username} - ${user.phonenumber} - ${user.password}`;
                list.appendChild(li);
            });
        })
        .catch(error => console.error("Error fetching users:", error));

    const signupForm = document.querySelector(".sign-input");
    signupForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = signupForm.querySelector('input[type="email"]').value;
        const username = signupForm.querySelector('input[placeholder="Username"]').value;
        const phonenumber = signupForm.querySelector('input[placeholder="Phone Number"]').value;
        const password = signupForm.querySelector('input[type="password"]').value;
        const confirmPassword = signupForm.querySelector('input[placeholder="Confirm Password"]').value;

        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }
        const response = await fetch("http://localhost:8000/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, username, phonenumber, password })
        });
        const data = await response.json();
        alert(data.message || data.error);
    });

    const loginForm = document.querySelector(".log-input");
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = loginForm.querySelector('input[type="text"]').value;
        const password = loginForm.querySelector('input[type="password"]').value;

        const response = await fetch("http://localhost:8000/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (data.user) {
            // redirect to home page
            window.location.href = "../index.html";
        } else {
            alert(data.error);
        }
    });
});
