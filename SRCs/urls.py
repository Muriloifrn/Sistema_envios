from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', lambda request: redirect('login'), name='root_redirect'),
    path('login', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/unidades/novo', views.cadastro_unidade, name='cadastro_unidade'),
    path('home/unidades', views.unidade, name='unidade'),
    path('home/usuarios', views.user, name='user'),
    path('home/usuarios/novo', views.cadastro_user, name='cadastro_user'),
    path('home', views.home, name='home'),
    path('home/novo_envio', views.cadastro_envio, name='cadastro_envio'),
    path('home/rateio', views.rateio, name='rateio'),
    path('home/dashboard', views.dashboard, name='dashboard'),
    path('home/exportar', views.exportar_rateio, name='exportar_rateio'),
    path('home/acompanhamento_envio', views.acompanhamento, name='acompanhamento'),
    path('home/unidade/editar', views.editar_unidade, name='editar_unidade'),
    path('home/unidade/excluir/<int:unidade_id>/', views.excluir_unidade, name='excluir_unidade'),
    path('home/unidades/excluir-multiplo/', views.excluir_unidades_multiplo, name='excluir_unidades_multiplo'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:usuario_id>/', views.excluir_usuario, name='excluir_usuario'),



]
