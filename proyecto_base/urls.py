from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    #pasamos el parametro <int:pag> para la paginacion
    path('',views.index),
    path('/', views.index),
    path('populate/', views.populateDatabase),
    path('admin/',admin.site.urls),
    path('cargarsr/',views.cargarSR),
    path('recomendar/',views.recomendar_animes),
    path('mejoresanimes/',views.mejores_animes),
    path('genero/',views.peliculaPorGenero)
    ]
