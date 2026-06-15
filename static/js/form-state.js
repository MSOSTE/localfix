(function () {
    const storageKey = `localfix-form:${window.location.pathname}`;

    window.saveFormState = function () {
        const form = document.querySelector(".preserve-form-state");
        if (!form) {
            return;
        }

        const data = {};
        const fields = form.querySelectorAll("input, textarea, select");

        fields.forEach((field) => {
            if (!field.name || field.type === "password" || field.type === "hidden") {
                return;
            }
            data[field.name] = field.value;
        });

        sessionStorage.setItem(storageKey, JSON.stringify(data));
    };

    document.addEventListener("DOMContentLoaded", function () {
        const saved = sessionStorage.getItem(storageKey);
        const form = document.querySelector(".preserve-form-state");

        if (!saved || !form) {
            return;
        }

        const data = JSON.parse(saved);
        Object.entries(data).forEach(([name, value]) => {
            const field = form.querySelector(`[name="${name}"]`);
            if (field && field.type !== "password") {
                field.value = value;
            }
        });

        sessionStorage.removeItem(storageKey);
    });
})();
