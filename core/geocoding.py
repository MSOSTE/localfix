import json
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


def format_address(data):
    address = data.get("address", {})
    road = address.get("road") or address.get("pedestrian") or address.get("footway")
    house_number = address.get("house_number")
    city = address.get("city") or address.get("town") or address.get("village") or address.get("municipality")
    postcode = address.get("postcode")

    street_parts = [part for part in [road, house_number] if part]
    location_parts = []
    if street_parts:
        location_parts.append(" ".join(street_parts))
    if city:
        location_parts.append(city)
    if postcode:
        location_parts.append(postcode)

    # Prefer a short address instead of the full Nominatim display string.
    return ", ".join(location_parts) or data.get("display_name", "")


def geocode_address(address):
    if not address:
        return None

    params = urlencode({"q": address, "format": "json", "limit": 1, "accept-language": "lv"})
    # Nominatim requires a real User-Agent.
    request = Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": settings.GEOCODER_USER_AGENT},
    )

    try:
        with urlopen(request, timeout=settings.GEOCODER_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if not data:
        return None

    try:
        return Decimal(data[0]["lat"]), Decimal(data[0]["lon"])
    except (KeyError, InvalidOperation):
        return None


def reverse_geocode_coordinates(latitude, longitude):
    if latitude is None or longitude is None:
        return ""

    params = urlencode(
        {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "zoom": 18,
            "addressdetails": 1,
            "accept-language": "lv",
        }
    )
    # Reverse geocoding fills the address after a map click.
    request = Request(
        f"https://nominatim.openstreetmap.org/reverse?{params}",
        headers={"User-Agent": settings.GEOCODER_USER_AGENT},
    )

    try:
        with urlopen(request, timeout=settings.GEOCODER_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    return format_address(data)
