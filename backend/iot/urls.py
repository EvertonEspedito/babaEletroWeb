
from django.urls import path
from . import views

urlpatterns = [
    path("heartbeat/", views.heartbeat, name="heartbeat"),
    path("alert/", views.create_alert, name="create_alert"),
    path("state/", views.dashboard_state, name="dashboard_state"),
]
