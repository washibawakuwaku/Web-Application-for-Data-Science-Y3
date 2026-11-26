"""
API views.  Same endpoints as the FastAPI backend, so the Streamlit
frontend works with either one.
"""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ml import service

from .models import PredictionLog


@require_GET
def health(request):
    return JsonResponse({"status": "ok", "backend": "django"})


@require_GET
def schema(request):
    return JsonResponse(service.get_schema())


@require_GET
def data(request):
    limit = int(request.GET.get("limit", 100))
    return JsonResponse(service.get_data(limit))


@require_GET
def metrics(request):
    report = service.get_metrics()
    if report is None:
        return JsonResponse({"detail": "Model is not trained yet."}, status=404)
    return JsonResponse(report)


@csrf_exempt
@require_POST
def train(request):
    return JsonResponse(service.train_model())


@csrf_exempt
@require_POST
def predict(request):
    try:
        body = json.loads(request.body or "{}")
        features = body["features"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"detail": 'Send JSON like {"features": {...}}'}, status=400)
    try:
        result = service.make_prediction(features)
    except RuntimeError as e:
        return JsonResponse({"detail": str(e)}, status=409)
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=422)

    PredictionLog.objects.create(
        input_data=features,
        prediction=str(result["prediction"]),
        probabilities=result.get("probabilities"),
    )
    return JsonResponse(result)


@require_GET
def prediction_history(request):
    logs = PredictionLog.objects.all()[:50]
    return JsonResponse({"items": [
        {"created_at": log.created_at.isoformat(), "input": log.input_data,
         "prediction": log.prediction, "probabilities": log.probabilities}
        for log in logs
    ]})


# TODO: add views for the other features in your scope sheet.
