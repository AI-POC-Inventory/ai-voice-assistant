from django.urls import path
from .views import config_page
from .views import edit_assistant
from .views import delete_assistant

urlpatterns = [
    path("", config_page, name="config"),
    path("edit/<int:id>/", edit_assistant, name="edit_assistant"),
    path("delete/<int:id>/", delete_assistant, name="delete_assistant"),


]
