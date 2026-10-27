from django.urls import path
from . import views

# Montado em /api/assistidas/
urlpatterns = [
    path('adicionar/', views.adicionar, name='adicionar_assistida'),
]
