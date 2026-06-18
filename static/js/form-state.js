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

    window.changeLanguage = function (select) {
        window.saveFormState();

        const form = select.form;
        const nextInput = form.querySelector('input[name="next"]');
        const language = select.value;
        // Replace the current language prefix before redirecting.
        const path = window.location.pathname.replace(/^\/(lv|en)(?=\/|$)/, "");
        const nextPath = `/${language}${path || "/"}${window.location.search}`;

        if (nextInput) {
            nextInput.value = nextPath;
        }

        form.submit();
    };

    window.setLanguage = function (language) {
        const select = document.querySelector(".language-select");
        if (!select) {
            return;
        }

        select.value = language;
        window.changeLanguage(select);
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
