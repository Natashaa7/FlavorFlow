document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".logout-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {

            e.preventDefault();

            Swal.fire({
                title: "Logout?",
                text: "You will need to login again to continue.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#64893a",
                cancelButtonColor: "#6c757d",
                confirmButtonText: "Yes, logout",
                cancelButtonText: "Cancel",
                background: "#f5eddd",
                color: "#6a4d36",

                didOpen: (popup) => {
                    popup.style.borderRadius = "30px";
                }
            }).then((result) => {

                if (result.isConfirmed) {
                    window.location.href = "/logout";
                }

            });
        });
    });

});
