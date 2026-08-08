from django.contrib import admin 
from .models import Servico, Cliente, Agendamento

# Register your models here.


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "preco",
        "duracao",
        "ativo",
    )

    list_filter = ("ativo",)

    search_fields = ("nome",)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "telefone",
        "email",
    )

    search_fields = (
        "nome",
        "telefone",
        "email",
    )


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = (
        "cliente",
        "servico",
        "data",
        "horario",
        "status",
    )

    list_filter = (
        "status",
        "data",
        "servico",
    )

    search_fields = (
        "cliente__nome",
        "cliente__telefone",
    )
    ordering = ("-data", "horario")