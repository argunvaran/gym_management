from django.urls import path
from . import views

urlpatterns = [
    path('test-page/', views.test_page, name='test_page'),
]
