from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("cadastrar-agendamento/", views.cadastrar_agendamento, name="cadastrar_agendamento"),
    path("agendamento-confirmado/<str:token>/", views.agendamento_confirmado, name="agendamento_confirmado"),
    path("horarios-disponiveis/", views.consultar_horarios, name="consultar_horarios"),
    path("listar-servicos/", views.listar_servicos, name="listar_servicos"),
    path("galeria/", views.galeria, name="galeria"),
    path("painel-agendamentos/", views.painel_agendamentos, name="painel_agendamentos"),
    path("painel-agendamentos/<int:id>/status/", views.atualizar_status_agendamento, name="atualizar_status_agendamento"),
    path("excluir-servico/<int:id>/", views.excluir_servico, name="excluir_servico"),
    path("listar-clientes/", views.listar_clientes, name="listar_clientes"),
    path("editar-cliente/<int:id>/", views.editar_cliente, name="editar_cliente"),
]