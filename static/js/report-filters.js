(function () {
    let map = null;

    function readMapData() {
        const dataTag = document.getElementById("report-map-data");
        if (!dataTag) {
            return [];
        }

        try {
            return JSON.parse(dataTag.textContent);
        } catch (error) {
            return [];
        }
    }

    function filterMapReports(reports) {
        const statusFilter = document.getElementById("map-status-filter");
        const categoryFilters = document.querySelectorAll(".map-category-filters input[type='checkbox']");

        if (!statusFilter && categoryFilters.length === 0) {
            return reports;
        }

        const selectedStatus = statusFilter ? statusFilter.value : "";
        const selectedCategories = Array.from(categoryFilters)
            .filter((input) => input.checked)
            .map((input) => input.value);

        return reports.filter((report) => {
            const statusMatches = !selectedStatus || report.statusValue === selectedStatus;
            const categoryMatches = selectedCategories.includes(String(report.categoryId));
            return statusMatches && categoryMatches;
        });
    }

    function initReportMap() {
        const mapElement = document.getElementById("reports-map");
        const reports = filterMapReports(readMapData());

        if (!mapElement || !window.L) {
            return;
        }

        if (map) {
            // Rebuild the map after filters change.
            map.remove();
        }

        map = L.map(mapElement);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; OpenStreetMap contributors",
        }).addTo(map);

        const bounds = [];
        reports.forEach((report) => {
            const marker = L.circleMarker([report.lat, report.lng], {
                color: "#ffffff",
                fillColor: report.categoryColor || "#263e8b",
                fillOpacity: 1,
                radius: 9,
                weight: 2,
            }).addTo(map);
            const title = escapeHtml(report.title);
            const address = escapeHtml(report.address);
            const status = escapeHtml(report.status);
            const category = escapeHtml(report.category || "");
            marker.bindPopup(`<strong>${title}</strong><br>${category}<br>${address}<br>${status}`);
            marker.on("click", () => {
                // First click opens the popup, second click opens the report.
                if (marker.isPopupOpen()) {
                    window.location.href = report.url;
                    return;
                }

                marker.openPopup();
            });
            bounds.push([report.lat, report.lng]);
        });

        if (bounds.length === 0) {
            map.setView([56.9496, 24.1052], 12);
        } else if (bounds.length === 1) {
            map.setView(bounds[0], 15);
        } else {
            map.fitBounds(bounds, { padding: [24, 24] });
        }
    }

    function escapeHtml(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function bindAjaxFilters() {
        const form = document.getElementById("report-filter-form");
        const results = document.getElementById("report-results");

        if (!form || !results) {
            return;
        }

        window.reloadReportResults = function (url = null, updateHistory = false) {
            // Filters update the list without reloading the whole page.
            const targetUrl = url || `${form.dataset.ajaxUrl}${window.location.search}`;
            fetch(targetUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } })
                .then((response) => response.json())
                .then((data) => {
                    results.innerHTML = data.html;
                    if (updateHistory) {
                        window.history.replaceState({}, "", targetUrl);
                    }
                    initReportMap();
                });
        };

        form.addEventListener("submit", (event) => {
            event.preventDefault();
            const params = new URLSearchParams(new FormData(form));
            window.reloadReportResults(`${form.dataset.ajaxUrl}?${params.toString()}`, true);
        });

        form.querySelectorAll("select, input[type='checkbox']").forEach((field) => {
            field.addEventListener("change", () => form.requestSubmit());
        });

        results.addEventListener("click", (event) => {
            const link = event.target.closest(".pagination a");
            if (!link) {
                return;
            }
            event.preventDefault();
            window.reloadReportResults(link.href, true);
        });
    }

    function bindMapFilters() {
        const controls = document.querySelectorAll("#map-status-filter, .map-category-filters input[type='checkbox']");
        controls.forEach((control) => {
            control.addEventListener("change", initReportMap);
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        initReportMap();
        bindAjaxFilters();
        bindMapFilters();
    });
})();
