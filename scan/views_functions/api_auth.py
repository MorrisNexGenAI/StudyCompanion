from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json

@csrf_exempt
@require_POST
def api_login(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return JsonResponse({"success": False, "error": "Missing credentials"}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is None or not user.is_active:
        return JsonResponse({"success": False, "error": "Invalid credentials"}, status=401)

    login(request, user)

    return JsonResponse({
        "success": True,
        "username": user.username,
        "is_admin": user.is_staff,
    })


@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({"success": True})


@require_GET
def api_me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False}, status=401)

    return JsonResponse({
        "authenticated": True,
        "username": request.user.username,
        "is_admin": request.user.is_staff,
    })
