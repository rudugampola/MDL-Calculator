from django.urls import path

from . import views

app_name = "calculate"

urlpatterns = [
    path("", views.import_excel, name="import_excel"),
]
