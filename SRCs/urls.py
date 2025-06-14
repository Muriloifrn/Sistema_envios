from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('home/unidades/novo', views.cadastro_unidade, name='cadastro_unidade'),
    path('home/unidade', views.unidade, name='unidade'),
    path('home/usuarios', views.user, name='user'),
    path('home/usuarios/novo', views.cadastro_user, name='cadastro_user'),
    path('home', views.home, name='home'),
    path('home/novo_envio', views.cadastro_envio, name='cadastro_envio'),
    path('home/rateio', views.rateio, name='rateio'),
    path('home/dashboard', views.dashboard, name='dashboard')
]
 