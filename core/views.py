from datetime import date, datetime, time, timedelta
from urllib.parse import quote
from django.db.models import Sum

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from .forms import AgendamentoClienteForm, AgendamentoForm, ClienteForm, ReagendamentoForm
from .models import Agendamento, Cliente, Servico


def horarios_disponiveis(data_atendimento, servico=None, agendamento_id= None):
    if data_atendimento.weekday() == 6:
        return []

    inicio, fim = (8, 16) if data_atendimento.weekday() == 5 else (8, 19)

    # Duração do serviço que está sendo agendado. Se ainda não foi
    # escolhido (ex.: cliente ainda não selecionou o serviço),
    # assume 30 min como valor conservador — o mínimo bloco possível.
    duracao_desejada = servico.duracao if servico else 30

    # Monta os intervalos (início, fim) já ocupados no dia, usando
    # a duração de CADA agendamento existente (não um bloco fixo).
    agendamentos_do_dia = (
        Agendamento.objects.filter(data=data_atendimento)
        .exclude(status="cancelado")
        .select_related("servico")
    )
    if agendamento_id:
        agendamentos_do_dia = agendamentos_do_dia.exclude(pk= agendamento_id)
    
    ocupados_intervalos = []
    for agendamento in agendamentos_do_dia:
        inicio_ocupado = datetime.combine(data_atendimento, agendamento.horario)
        fim_ocupado = inicio_ocupado + timedelta(minutes=agendamento.servico.duracao)
        ocupados_intervalos.append((inicio_ocupado, fim_ocupado))

    agora = datetime.now()

    horarios = []
    atual = datetime.combine(data_atendimento, time(inicio))
    limite = datetime.combine(data_atendimento, time(fim))
    while atual < limite:
        fim_atendimento = atual + timedelta(minutes=duracao_desejada)

        # O atendimento não pode ultrapassar o horário de fechamento.
        if fim_atendimento > limite:
            break

        # Se a data pedida é hoje, não mostra horários que já
        # passaram (ou que estão prestes a começar agora mesmo).
        if data_atendimento == date.today() and atual <= agora:
            atual += timedelta(minutes=30)
            continue

        # Sobrepõe com algum agendamento existente?
        conflita = any(
            atual < fim_ocupado and fim_atendimento > inicio_ocupado
            for inicio_ocupado, fim_ocupado in ocupados_intervalos
        )
        if not conflita:
            horarios.append(atual.strftime("%H:%M"))

        atual += timedelta(minutes=30)

    return horarios


def link_whatsapp(telefone, mensagem):
    numero = "".join(caractere for caractere in telefone if caractere.isdigit())
    if not numero.startswith("55"):
        numero = f"55{numero}"
    return f"https://wa.me/{numero}?text={quote(mensagem)}"


def index(request):
    servicos = Servico.objects.filter(ativo=True).order_by("id")[:3]
    return render(request, "core/index.html", {"servicos": servicos})


def erro_404(request, exception):
    return render(request, "core/404.html", status=404)


def _admin_required(view_func):
    return user_passes_test(
        lambda user: user.is_active and user.is_staff,
        login_url="/admin/login/",
    )(view_func)


def cadastrar_agendamento(request):
    initial, horarios = {}, []
    servico_id = request.POST.get("servico") or request.GET.get("servico")
    servico = None
    if servico_id:
        initial["servico"] = servico_id
        servico = Servico.objects.filter(pk=servico_id, ativo=True).first()

    data_formulario = request.POST.get("data") or request.GET.get("data")
    if data_formulario:
        try:
            horarios = horarios_disponiveis(date.fromisoformat(data_formulario), servico)
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
            # Mostra o aviso (não bloqueante) de telefone já
            # cadastrado com outro nome, se houver. Como isso vem
            # depois do redirect, a mensagem aparece na próxima
            # página graças ao framework de mensagens do Django.
            if form.aviso_telefone:
                messages.warning(request, form.aviso_telefone)
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

    servico_id = request.GET.get("servico")
    servico = Servico.objects.filter(pk=servico_id, ativo=True).first() if servico_id else None

    return JsonResponse({"horarios": horarios_disponiveis(data_atendimento, servico), "mensagem": ""})


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



@_admin_required
def painel_agendamentos(request):

    hoje = date.today()

    status_permitidos = {valor for valor, _ in Agendamento.STATUS_CHOICES}
    status_filtro = (request.GET.get("status") or "").strip()

    if status_filtro and status_filtro not in status_permitidos:
        status_filtro = None

    agendamentos = (
    Agendamento.objects
    .select_related("cliente", "servico")
    .filter(data__gte=hoje)
    .order_by("data", "horario")
)

    if status_filtro:
        agendamentos = agendamentos.filter(status=status_filtro)
    else:
        agendamentos = agendamentos.exclude(status="concluido")

    lembretes = (
        Agendamento.objects
        .select_related("cliente", "servico")
        .filter(
            data=hoje + timedelta(days=1)
        )
        .exclude(status="cancelado")
        .exclude(status="concluido")
        .order_by("horario")
    )
    for agendamento in lembretes:

        mensagem = (
            f"Olá, {agendamento.cliente.nome}! Passando para lembrar do seu horário amanhã, "
            f"{agendamento.data.strftime('%d/%m')} às {agendamento.horario.strftime('%H:%M')}, "
            f"na Auto Corte."
        )

        agendamento.whatsapp_url = link_whatsapp(
            agendamento.cliente.telefone,
            mensagem
        )

    faturamento_mes = (
        Agendamento.objects
        .filter(
            data__year=hoje.year,
            data__month=hoje.month,
            status="concluido",
        )
        .aggregate(total=Sum("preco"))["total"]
        or 0
    )

    return render(
        request,
        "core/painel_agendamentos.html",
        {
            "agendamentos": agendamentos,
            "lembretes": lembretes,
            "faturamento_mes": faturamento_mes,
        },
    )

@require_POST
@_admin_required
def atualizar_status_agendamento(request, id):
    try:
        id = int(id)
    except (TypeError, ValueError):
        messages.error(request, "Identificador inválido.")
        return redirect("painel_agendamentos")

    agendamento = get_object_or_404(Agendamento, id=id)

    status = (request.POST.get("status") or "").strip()
    status_permitidos = dict(Agendamento.STATUS_CHOICES)

    if status not in status_permitidos:
        messages.error(request, "Status inválido.")
        return redirect("painel_agendamentos")

    agendamento.status = status

    try:
        agendamento.full_clean()
        agendamento.save(update_fields=["status"])

        messages.success(
            request,
            f"Status do agendamento {agendamento} alterado para '{status}'."
        )

    except ValidationError:
        messages.error(
            request,
            "Não é possível alterar o status porque este horário "
            "conflita com outro agendamento."
        )

    return redirect("painel_agendamentos")

@_admin_required
def listar_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, "core/listar_clientes.html", {"clientes": clientes})


@_admin_required
def editar_cliente(request, id):
    try:
        id = int(id)
    except (TypeError, ValueError):
        messages.error(request, "Identificador inválido.")
        return redirect("listar_clientes")

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


def reagendar_agendamento(request, token):
    agendamento = get_object_or_404(Agendamento, token=token)

    data_para_horarios = agendamento.data

    if request.method == "POST":
        data_enviada = request.POST.get("nova_data")

        if data_enviada:
            try:
                data_para_horarios = date.fromisoformat(data_enviada)
            except ValueError:
                pass

    horarios = horarios_disponiveis(
        data_para_horarios,
        agendamento.servico,
        agendamento.id,
    )

    if request.method == "POST":
        form = ReagendamentoForm(
            request.POST,
            instance=agendamento,
            horarios_disponiveis=horarios,
        )

        if form.is_valid():

            agendamento.data = form.cleaned_data["nova_data"]
            agendamento.horario = form.cleaned_data["novo_horario"]

            try:
                agendamento.full_clean()
                agendamento.save()

            except ValidationError as erro:
                form.add_error(
                    "novo_horario",
                    erro.message_dict.get("horario", erro.messages)
                )

            else:
                messages.success(
                    request,
                    "Agendamento reagendado com sucesso!"
                )
                return redirect(
                    "agendamento_confirmado",
                    token=agendamento.token
                )

    else:
        form = ReagendamentoForm(
            instance=agendamento,
            horarios_disponiveis=horarios,
        )

    return render(
        request,
        "core/reagendar_agendamento.html",
        {
            "form": form,
            "agendamento": agendamento,
        },
    )


def politica_privacidade(request):
    return render(request, "core/politica_privacidade.html")

