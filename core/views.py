from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from .forms import AgendamentoClienteForm, AgendamentoForm, ClienteForm, ServicoForm
from .models import Agendamento, Cliente, Servico


def index(request):
    return render(request, "core/index.html")


def cadastrar_cliente(request):
    form = ClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("listar_clientes")
    return render(request, "core/cadastrar_cliente.html", {"form": form})


def cadastrar_servico(request):
    form = ServicoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("listar_servicos")
    return render(request, "core/cadastrar_servico.html", {"form": form})


def cadastrar_agendamento(request):
    form = AgendamentoClienteForm(request.POST or None)
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
        agendamento.save()
        messages.success(request, "Agendamento realizado com sucesso! Te esperamos na Auto Corte.")
        return redirect("index")

    return render(request, "core/cadastrar_agendamento.html", {"form": form})


def listar_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, "core/listar_clientes.html", {"clientes": clientes})


def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("listar_clientes")
    return render(request, "core/editar_cliente.html", {"form": form})


def excluir_cliente(request, id):
    if request.method == "POST":
        get_object_or_404(Cliente, id=id).delete()
    return redirect("listar_clientes")


def listar_servicos(request):
    servicos = Servico.objects.all()
    return render(request, "core/listar_servicos.html", {"servicos": servicos})


def editar_servico(request, id):
    servico = get_object_or_404(Servico, id=id)
    form = ServicoForm(request.POST or None, instance=servico)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("listar_servicos")
    return render(request, "core/editar-servicos.html", {"form": form})


def excluir_servico(request, id):
    if request.method == "POST":
        get_object_or_404(Servico, id=id).delete()
    return redirect("listar_servicos")


def listar_agendamentos(request):
    agendamentos = Agendamento.objects.select_related("cliente", "servico")
    return render(
        request,
        "core/listar_agendamentos.html",
        {"agendamentos": agendamentos},
    )


def editar_agendamento(request, id):
    agendamento = get_object_or_404(Agendamento, id=id)
    form = AgendamentoForm(request.POST or None, instance=agendamento)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("listar_agendamentos")
    return render(request, "core/editar_agendamento.html", {"form": form})


def excluir_agendamento(request, id):
    if request.method == "POST":
        get_object_or_404(Agendamento, id=id).delete()
    return redirect("listar_agendamentos")
