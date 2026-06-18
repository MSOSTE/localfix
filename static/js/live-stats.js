(function () {
    document.addEventListener("DOMContentLoaded", function () {
        const panels = document.querySelectorAll("[data-live-stats-url]");
        const firstPanel = panels[0];

        if (!firstPanel || !window.EventSource) {
            return;
        }

        const source = new EventSource(firstPanel.dataset.liveStatsUrl);
        const statuses = document.querySelectorAll("[data-live-status]");
        let lastStats = null;

        source.onmessage = function (event) {
            // SSE sends fresh report counts from Django.
            const stats = JSON.parse(event.data);
            const hasChanged = lastStats !== null && JSON.stringify(stats) !== JSON.stringify(lastStats);
            panels.forEach((panel) => {
                Object.entries(stats).forEach(([key, value]) => {
                    const element = panel.querySelector(`[data-stat="${key}"]`);
                    if (element) {
                        element.textContent = value;
                    }
                });
            });
            lastStats = stats;

            if (hasChanged && typeof window.reloadReportResults === "function") {
                window.reloadReportResults();
            }

            statuses.forEach((status) => {
                status.classList.remove("is-offline");
            });
        };

        source.onerror = function () {
            statuses.forEach((status) => {
                status.classList.add("is-offline");
            });
        };
    });
})();
