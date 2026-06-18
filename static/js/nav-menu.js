(function () {
    document.addEventListener("DOMContentLoaded", function () {
        const button = document.querySelector(".menu-toggle");
        const nav = document.getElementById("main-nav");

        if (!button || !nav) {
            return;
        }

        button.addEventListener("click", function () {
            const isOpen = nav.classList.toggle("is-open");
            button.setAttribute("aria-expanded", String(isOpen));
        });

        nav.querySelectorAll("a, button").forEach((item) => {
            item.addEventListener("click", function () {
                nav.classList.remove("is-open");
                button.setAttribute("aria-expanded", "false");
            });
        });
    });
})();
