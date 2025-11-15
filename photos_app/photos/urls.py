from django.urls import path
from .views import PhotoListCreateView, PhotoDetailView, PhotoShareView

urlpatterns = [
    path('', PhotoListCreateView.as_view(), name='photo-list-create'),
    path('<int:pk>/', PhotoDetailView.as_view(), name='photo-detail'),
    path('share/', PhotoShareView.as_view(), name='photo-share'),
]