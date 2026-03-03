# backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ 앱 라우팅은 include만! (views 직접 import 금지)
    path("api/accounts/", include("accounts.urls")),
    path("api/wellness/", include("wellness.urls")),
    path("api/usage/", include("usage.urls")),
]
