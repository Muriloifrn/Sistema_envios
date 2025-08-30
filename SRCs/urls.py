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
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path("usuarios/excluir/", views.excluir_usuario, name="excluir_usuario"),
    path('home/acompanhamento/detalhes/<str:etiqueta>', views.detalhe_envio, name='detalhe_envio'),
    path('home/unidades/importar', views.importar_unidade, name='importar_unidade'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('alterar-foto/', views.alterar_foto, name='alterar_foto'),
    path('usuarios/detalhes/<int:usuario_id>/', views.detalhes_usuario, name='detalhes_usuario'),
    path('unidades/detalhes/<int:unidade_id>/', views.detalhes_unidade, name='detalhes_unidade'),
    path('unidades/editar/<int:unidade_id>/', views.editar_unidade_ajax, name='editar_unidade_ajax'),
    path('unidades/excluir/', views.excluir_unidades_ajax, name='excluir_unidades_ajax'),



]
