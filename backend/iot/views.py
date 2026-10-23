
import json
import hmac

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Alert, DeviceStatus


DEVICE_NAME = "pico-w-baba-eletronica"


def add_cors_headers(request, response):
    origin = request.headers.get("Origin", "")

    if origin == settings.IOT_ALLOWED_ORIGIN:
        response["Access-Control-Allow-Origin"] = origin
        response["Vary"] = "Origin"

    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = (
        "Content-Type, X-Device-Key, X-Dashboard-Token"
    )
    response["Cache-Control"] = "no-store"

    return response


def json_response(request, data, status=200):
    response = JsonResponse(data, status=status)
    return add_cors_headers(request, response)


def valid_key(received, expected):
    return bool(received and expected) and hmac.compare_digest(
        received,
        expected
    )


def device_authorized(request):
    return valid_key(
        request.headers.get("X-Device-Key", ""),
        settings.IOT_DEVICE_KEY
    )


def dashboard_authorized(request):
    return valid_key(
        request.headers.get("X-Dashboard-Token", ""),
        settings.IOT_DASHBOARD_TOKEN
    )


def read_json(request):
    try:
        data = json.loads(request.body or b"{}")
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def heartbeat(request):
    if request.method == "OPTIONS":
        return json_response(request, {})

    if not device_authorized(request):
        return json_response(
            request,
            {"error": "Dispositivo nao autorizado"},
            401
        )

    data = read_json(request)

    if data is None:
        return json_response(
            request,
            {"error": "JSON invalido"},
            400
        )

    try:
        level = int(data.get("sound_level", 0))
        level = max(0, min(level, 65535))
    except (ValueError, TypeError):
        return json_response(
            request,
            {"error": "Nivel sonoro invalido"},
            400
        )

    status, _ = DeviceStatus.objects.get_or_create(
        name=DEVICE_NAME
    )

    status.last_seen = timezone.now()
    status.last_sound_level = level
    status.save(update_fields=["last_seen", "last_sound_level"])

    return json_response(request, {
        "ok": True,
        "online": True,
        "last_seen": status.last_seen.isoformat()
    })


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def create_alert(request):
    if request.method == "OPTIONS":
        return json_response(request, {})

    if not device_authorized(request):
        return json_response(
            request,
            {"error": "Dispositivo nao autorizado"},
            401
        )

    data = read_json(request)

    if data is None:
        return json_response(
            request,
            {"error": "JSON invalido"},
            400
        )

    message = str(
        data.get("message", "Som elevado detectado")
    )[:240]

    alert_type = str(
        data.get("type", "possible_cry")
    )[:40]

    try:
        level = int(data.get("sound_level", 0))
        level = max(0, min(level, 65535))
    except (ValueError, TypeError):
        return json_response(
            request,
            {"error": "Nivel sonoro invalido"},
            400
        )

    alert = Alert.objects.create(
        alert_type=alert_type,
        message=message,
        sound_level=level
    )

    status, _ = DeviceStatus.objects.get_or_create(
        name=DEVICE_NAME
    )
    status.last_seen = timezone.now()
    status.last_sound_level = level
    status.save(update_fields=["last_seen", "last_sound_level"])

    return json_response(request, {
        "ok": True,
        "alert": {
            "id": alert.id,
            "message": alert.message,
            "sound_level": alert.sound_level,
            "created_at": alert.created_at.isoformat()
        }
    }, 201)


@require_http_methods(["GET", "OPTIONS"])
def dashboard_state(request):
    if request.method == "OPTIONS":
        return json_response(request, {})

    if not dashboard_authorized(request):
        return json_response(
            request,
            {"error": "Token do painel invalido"},
            401
        )

    status = DeviceStatus.objects.filter(
        name=DEVICE_NAME
    ).first()

    online = bool(
        status and
        status.last_seen and
        (timezone.now() - status.last_seen).total_seconds() < 45
    )

    recent_alerts = Alert.objects.order_by("-created_at")[:30]

    return json_response(request, {
        "online": online,
        "last_seen": (
            status.last_seen.isoformat()
            if status and status.last_seen else None
        ),
        "sound_level": (
            status.last_sound_level if status else 0
        ),
        "alerts": [
            {
                "id": alert.id,
                "type": alert.alert_type,
                "message": alert.message,
                "sound_level": alert.sound_level,
                "timestamp": alert.created_at.isoformat()
            }
            for alert in recent_alerts
        ]
    })
