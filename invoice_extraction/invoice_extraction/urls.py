from django.contrib import admin
from django.urls import path
from .views import AnalyzeImageView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('analyze-image/', AnalyzeImageView.as_view(), name='analyze-image'),  # ✅ CORRECT
]
