from datetime import date, datetime, time, timedelta
from urllib.parse import quote

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from .forms import AgendamentoClienteForm, AgendamentoForm, ClienteForm
from .models import Agendamento, Cliente, Servico


def horarios_disponiveis(data_atendimento):
    if data_atendimento.weekday() == 6:
        return []

    inicio, fim = (8, 16) if data_atendimento.weekday() == 5 else (8, 19)
    ocupados = set(
        Agendamento.objects.filter(data=data_atendimento)
        .exclude(status="cancelado")
        .values_list("horario", flat=True)
    )
    horarios = []
    atual = datetime.combine(data_atendimento, time(inicio))
    limite = datetime.combine(data_atendimento, time(fim))
    while atual < limite:
        horario = atual.time()
        if horario not in ocupados:
            horarios.append(atual.strftime("%H:%M"))
        atual += timedelta(minutes=30)
    return horarios


def link_whatsapp(telefone, mensagem):
    numero = "".join(caractere for caractere in telefone if caractere.isdigit())
    if not numero.startswith("55"):
        numero = f"55{numero}"
    return f"https://wa.me/{numero}?text={quote(mensagem)}"


def index(request):
    servicos = Servico.objects.filter(ativo=True)
    return render(request, "core/index.html", {"servicos": servicos})


def erro_404(request, exception):
    return render(request, "core/404.html", status=404)


def cadastrar_agendamento(request):
    initial, horarios = {}, []
    servico_id = request.GET.get("servico")
    if servico_id:
        initial["servico"] = servico_id

    data_formulario = request.POST.get("data") or request.GET.get("data")
    if data_formulario:
        try:
            horarios = horarios_disponiveis(date.fromisoformat(data_formulario))
        except ValueError:
            pass

    form = AgendamentoClienteForm(request.POST or None, initial=initial, horarios_disponiveis=horarios)
    if request.method == "POST" and form.is_valid():
        cliente = Cliente.objects.filter(telefone=form.cleaned_data["telefone"]).first()
        if cliente is None:
            cliente = Cliente.objects.create(
                nome=form.cleaned_data["nome"],
                telefone=form.cleaned_data["telefone"],
                email=form.cleaned_data["email"],
            )

        agendamento = form.save(commit=False)
        agendamento.cliente = cliente
        try:
            agendamento.full_clean()
            agendamento.save()
        except ValidationError as erro:
            form.add_error("horario", erro.message_dict.get("horario", erro.messages))
        else:
            return redirect("agendamento_confirmado", token=agendamento.token)

    return render(request, "core/cadastrar_agendamento.html", {"form": form})


@require_GET
def consultar_horarios(request):
    try:
        data_atendimento = date.fromisoformat(request.GET.get("data", ""))
    except ValueError:
        return JsonResponse({"horarios": [], "mensagem": "Escolha uma data válida."}, status=400)

    if data_atendimento < date.today():
        return JsonResponse({"horarios": [], "mensagem": "Escolha uma data futura."})
    if data_atendimento.weekday() == 6:
        return JsonResponse({"horarios": [], "mensagem": "Não atendemos aos domingos."})
    return JsonResponse({"horarios": horarios_disponiveis(data_atendimento), "mensagem": ""})


def agendamento_confirmado(request, token):
    agendamento = get_object_or_404(Agendamento, token=token)
    mensagem = (
        f"Olá, {agendamento.cliente.nome}! Seu agendamento na Auto Corte foi solicitado para "
        f"{agendamento.data.strftime('%d/%m/%Y')} às {agendamento.horario.strftime('%H:%M')}, "
        f"para {agendamento.servico.nome}."
    )
    return render(request, "core/agendamento_confirmado.html", {
        "agendamento": agendamento,
        "whatsapp_url": link_whatsapp(agendamento.cliente.telefone, mensagem),
    })


def galeria(request):
    return render(request, "core/galeria.html", {"servicos": Servico.objects.filter(ativo=True)})


@staff_member_required(login_url="/admin/login/")
def painel_agendamentos(request):
    hoje = date.today()
    agendamentos = Agendamento.objects.select_related("cliente", "servico").filter(data__gte=hoje).order_by("data", "horario")
    lembretes = agendamentos.filter(data=hoje + timedelta(days=1)).exclude(status="cancelado")
    for agendamento in lembretes:
        mensagem = (
            f"Olá, {agendamento.cliente.nome}! Passando para lembrar do seu horário amanhã, "
            f"{agendamento.data.strftime('%d/%m')} às {agendamento.horario.strftime('%H:%M')}, "
            f"na Auto Corte."
        )
        agendamento.whatsapp_url = link_whatsapp(agendamento.cliente.telefone, mensagem)
    return render(request, "core/painel_agendamentos.html", {"agendamentos": agendamentos, "lembretes": lembretes})


@require_POST
@staff_member_required(login_url="/admin/login/")
def atualizar_status_agendamento(request, id):
    agendamento = get_object_or_404(Agendamento, id=id)
    status = request.POST.get("status")
    if status in dict(Agendamento.STATUS_CHOICES):
        agendamento.status = status
        agendamento.full_clean()
        agendamento.save(update_fields=["status"])
    return redirect("painel_agendamentos")


@staff_member_required(login_url="/admin/login/")
def listar_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, "core/listar_clientes.html", {"clientes": clientes})


@staff_member_required(login_url="/admin/login/")
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("listar_clientes")
    return render(request, "core/editar_cliente.html", {"form": form})


def listar_servicos(request):
    servicos = Servico.objects.all()
    return render(request, "core/listar_servicos.html", {"servicos": servicos})


@staff_member_required(login_url="/admin/login/")
def excluir_servico(request, id):
    if request.method == "POST":
        get_object_or_404(Servico, id=id).delete()
    return redirect("listar_servicos")