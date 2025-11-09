# wellness/urls.py
# - wellness 관련 API 라우팅

from django.urls import path
from .views import EmotionMessageView, UserSettingsView

urlpatterns = [
    path("chatbot/message/", EmotionMessageView.as_view(), name="chatbot_message"),
    path("settings/", UserSettingsView.as_view(), name="user_settings"),
]
