(function () {
    function parseCoordinate(input) {
        const value = String(input.value || "").replace(",", ".");
        const number = Number.parseFloat(value);
        return Number.isFinite(number) ? number : null;
    }

    function setCoordinate(input, value) {
        input.value = Number(value).toFixed(6);
        input.dispatchEvent(new Event("input", { bubbles: true }));
    }

    function setAddress(input, value) {
        if (!value) {
            return;
        }
        input.value = value;
        input.dispatchEvent(new Event("input", { bubbles: true }));
    }

    document.addEventListener("DOMContentLoaded", () => {
        const mapElement = document.getElementById("location-picker-map");
        const addressInput = document.querySelector("[name='address']");
        const latitudeInput = document.querySelector("[name='latitude']");
        const longitudeInput = document.querySelector("[name='longitude']");

        if (!mapElement || !addressInput || !latitudeInput || !longitudeInput || !window.L) {
            return;
        }

        const defaultCenter = [56.9496, 24.1052];
        const startLatitude = parseCoordinate(latitudeInput);
        const startLongitude = parseCoordinate(longitudeInput);
        const hasStartLocation = startLatitude !== null && startLongitude !== null;
        const center = hasStartLocation ? [startLatitude, startLongitude] : defaultCenter;
        const map = L.map(mapElement).setView(center, hasStartLocation ? 15 : 12);
        let marker = null;

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; OpenStreetMap contributors",
        }).addTo(map);

        function placeMarker(latitude, longitude) {
            const location = [latitude, longitude];
            if (!marker) {
                marker = L.marker(location).addTo(map);
            } else {
                marker.setLatLng(location);
            }
        }

        function fillAddress(latitude, longitude) {
            const reverseUrl = mapElement.dataset.reverseUrl;
            if (!reverseUrl) {
                return;
            }

            // Ask Django to convert clicked coordinates into an address.
            const params = new URLSearchParams({ lat: latitude, lng: longitude });
            fetch(`${reverseUrl}?${params.toString()}`, { headers: { "X-Requested-With": "XMLHttpRequest" } })
                .then((response) => response.json())
                .then((data) => setAddress(addressInput, data.address))
                .catch(() => {});
        }

        if (hasStartLocation) {
            placeMarker(startLatitude, startLongitude);
        }

        map.on("click", (event) => {
            const { lat, lng } = event.latlng;
            // A map click fills both coordinate fields and the marker.
            setCoordinate(latitudeInput, lat);
            setCoordinate(longitudeInput, lng);
            placeMarker(lat, lng);
            fillAddress(lat, lng);
        });

        [latitudeInput, longitudeInput].forEach((input) => {
            input.addEventListener("input", () => {
                const latitude = parseCoordinate(latitudeInput);
                const longitude = parseCoordinate(longitudeInput);
                if (latitude === null || longitude === null) {
                    return;
                }
                placeMarker(latitude, longitude);
                map.setView([latitude, longitude], 15);
            });
        });
    });
})();
