from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("cadastrar-cliente/", views.cadastrar_cliente, name="cadastrar_cliente"),
    path("cadastrar-servico/", views.cadastrar_servico, name="cadastrar_servico"),
    path("cadastrar-agendamento/", views.cadastrar_agendamento, name="cadastrar_agendamento"),
    path("clientes/", views.listar_clientes, name="listar_clientes"),
    path("editar-cliente/<int:id>/", views.editar_cliente, name="editar_cliente"),
    path("excluir-cliente/<int:id>/", views.excluir_cliente, name="excluir_cliente"),
    path("listar-servicos/", views.listar_servicos, name="listar_servicos"),
    path("excluir-servico/<int:id>/", views.excluir_servico, name="excluir_servico"),
    path("editar-servico/<int:id>/", views.editar_servico, name="editar_servico"),
    path("listar-agendamentos/", views.listar_agendamentos, name="listar_agendamentos"),
    path("editar-agendamento/<int:id>/", views.editar_agendamento, name="editar_agendamento"),
    path("excluir-agendamento/<int:id>/", views.excluir_agendamento, name="excluir_agendamento"),
]
