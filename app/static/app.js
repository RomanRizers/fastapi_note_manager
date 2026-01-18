document.addEventListener("DOMContentLoaded", () => {
    const deletes = document.querySelectorAll(".delete-btn");

    deletes.forEach(btn => {
        btn.addEventListener("click", (e) => {
            if (!confirm("Удалить заметку?")) {
                e.preventDefault();
            }
        });
    });
});