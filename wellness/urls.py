# wellness/urls.py
from django.urls import path

urlpatterns = [
    path("chat/", __import__("wellness.views").views.ChatbotAPIView.as_view(), name="ai-chat"),
]
