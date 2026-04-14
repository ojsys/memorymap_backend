from django.shortcuts import redirect
from django.http import JsonResponse

def api_landing_page(request):
    return JsonResponse({
        "message": "Welcome to the Middlebelt Memorial API!",
        "documentation": "/api/docs", # Assuming you'll add Swagger/Redoc later
        "frontend_url": "https://web.middlebeltmemorial.org"
    })

def redirect_to_frontend(request):
    return redirect("https://web.middlebeltmemorial.org")