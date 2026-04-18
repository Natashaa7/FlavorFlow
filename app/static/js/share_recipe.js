document.addEventListener("DOMContentLoaded", () => {

    // =========================
    // ADD RECIPE
    // =========================
    const addForm = document.querySelector(".form-grid");

    if (addForm) {
        addForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const formData = new FormData(addForm);

            const response = await fetch("/add-recipe", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                await Swal.fire({
                    title: "Success!",
                    text: data.message,
                    icon: "success"
                });

                window.location.href = data.redirect;
            } else {
                Swal.fire({
                    title: "Error",
                    text: data.error,
                    icon: "error"
                });
            }
        });
    }


    // =========================
    // EDIT MODAL OPEN
    // =========================
    const modal = document.getElementById("editModal");
    const editForm = document.querySelector(".user-form");

    document.querySelectorAll(".edit").forEach(btn => {
        btn.addEventListener("click", () => {

            if (!modal) return;

            modal.style.display = "flex";

            document.getElementById("edit-id").value = btn.dataset.id;
            document.getElementById("edit-title").value = btn.dataset.title;
            document.getElementById("edit-description").value = btn.dataset.description;
            document.getElementById("edit-time").value = btn.dataset.time;
            document.getElementById("edit-difficulty").value = btn.dataset.difficulty;

            document.getElementById("current-image").src = btn.dataset.image;
            document.getElementById("current-file").href = btn.dataset.file;
        });
    });


    // =========================
    // CLOSE MODAL
    // =========================
    const closeBtn = document.getElementById("closeEditModal");
    const cancelBtn = document.getElementById("cancelEditModal");

    if (closeBtn) {
        closeBtn.addEventListener("click", () => modal.style.display = "none");
    }

    if (cancelBtn) {
        cancelBtn.addEventListener("click", () => modal.style.display = "none");
    }


    // =========================
    // UPDATE RECIPE
    // =========================
    if (editForm) {
        editForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const formData = new FormData(editForm);

            try {
                const response = await fetch("/update-recipe", {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    await Swal.fire({
                        title: "Success!",
                        text: data.message,
                        icon: "success"
                    });

                    window.location.href = data.redirect;
                } else {
                    Swal.fire({
                        title: "Error",
                        text: data.error || "Update failed",
                        icon: "error"
                    });
                }

            } catch (err) {
                Swal.fire({
                    title: "Error",
                    text: "Server error occurred",
                    icon: "error"
                });
            }
        });
    }


    // =========================
    // DELETE RECIPE
    // =========================
    document.querySelectorAll(".delete").forEach(btn => {
        btn.addEventListener("click", async () => {

            const recipeId = btn.dataset.id;

            const result = await Swal.fire({
                title: "Delete this recipe?",
                text: "This action cannot be undone.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Yes, delete it"
            });

            if (result.isConfirmed) {

                const formData = new FormData();
                formData.append("id", recipeId);

                const response = await fetch("/delete-recipe", {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    await Swal.fire("Deleted!", data.message, "success");
                    window.location.href = data.redirect;
                } else {
                    Swal.fire("Error", data.error, "error");
                }
            }
        });
    });


    // =========================
    // DOWNLOAD FILE
    // =========================
    document.querySelectorAll(".download").forEach(btn => {
        btn.addEventListener("click", () => {

            const fileUrl = btn.dataset.file;

            Swal.fire({
                title: "Download this recipe?",
                text: "The recipe file will be downloaded.",
                icon: "info",
                showCancelButton: true,
                confirmButtonText: "Yes, download"
            }).then((result) => {

                if (result.isConfirmed) {
                    const a = document.createElement("a");
                    a.href = fileUrl;
                    a.download = fileUrl.split("/").pop();
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }
            });
        });
    });

});
