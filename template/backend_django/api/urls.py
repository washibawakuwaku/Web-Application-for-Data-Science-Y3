from django.urls import path

from . import views

urlpatterns = [
    path("health", views.health),
    path("schema", views.schema),
    path("data", views.data),
    path("metrics", views.metrics),
    path("train", views.train),
    path("predict", views.predict),
    path("predictions", views.prediction_history),
]
