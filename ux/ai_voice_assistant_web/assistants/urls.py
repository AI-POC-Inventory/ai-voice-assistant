from django.urls import path
from .views import config_page
from .views import edit_assistant
from .views import delete_assistant
from .views import google_auth_start
from .views import google_auth_callback
from .views import google_callback
urlpatterns = [
    path("", config_page, name="config"),
    path("edit/<int:id>/", edit_assistant, name="edit_assistant"),
    path("delete/<int:id>/", delete_assistant, name="delete_assistant"),
    path("google/auth/start/", google_auth_start, name="google_auth_start"),
    path("google/callback/", google_callback, name="google_callback"),  # ✅ ADD THIS

]



