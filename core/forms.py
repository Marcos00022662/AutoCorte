import re
import datetime
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente, Servico, Agendamento


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "telefone", "email"]


class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ["nome", "descricao", "preco", "duracao", "ativo", "foto"]


class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ["cliente", "servico", "horario", "data"]
        widgets = {
            "data": forms.DateInput(
                attrs={
                    "class": "js-date-picker",
                    "autocomplete": "off",
                    "placeholder": "aaaa-mm-dd",
                    "type": "text",
                },
                format="%Y-%m-%d",
            ),
            "horario": forms.TimeInput(
                attrs={
                    "class": "js-time-picker",
                    "autocomplete": "off",
                    "placeholder": "hh:mm",
                    "type": "text",
                },
                format="%H:%M",
            ),
        }


class AgendamentoClienteForm(forms.ModelForm):

    nome = forms.CharField(max_length=100)
    telefone = forms.CharField(max_length=20)
    email = forms.EmailField(required=False)
    horario = forms.ChoiceField(choices=(), widget=forms.Select(attrs={"class": "js-time-picker"}))

    class Meta:
        model = Agendamento
        fields = [
            "nome",
            "telefone",
            "email",
            "servico",
            "horario",
            "data",
        ]

        widgets = {
            "data": forms.DateInput(
                attrs={
                    "class": "js-date-picker",
                    "autocomplete": "off",
                    "placeholder": "aaaa-mm-dd",
                    "type": "text",
                },
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, horarios_disponiveis=None, **kwargs):  # listagem de horarios do formulario
        super().__init__(*args, **kwargs)
        self.fields["servico"].queryset = Servico.objects.filter(ativo=True)
        horarios_disponiveis = horarios_disponiveis or []
        self.fields["horario"].choices = [(horario, horario) for horario in horarios_disponiveis]

    # Validação de Formulários
    def clean_horario(self):
        return datetime.datetime.strptime(self.cleaned_data["horario"], "%H:%M").time()

    def clean_data(self):
        data_atendimento = self.cleaned_data["data"]
        if data_atendimento < date.today():
            raise ValidationError("Escolha uma data futura.")
        return data_atendimento

    def clean_nome(self):
        nome = self.cleaned_data.get('nome', '').strip()
        if len(nome) < 3:
            raise ValidationError("O nome deve ter pelo menos 3 caracteres.")
        return nome

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '').strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        if telefone == '':
            raise ValidationError("O telefone é obrigatório.")

        if len(telefone) not in (10, 11):
            raise ValidationError("O telefone deve ter 10 ou 11 dígitos.")

        if not telefone.isdigit():
            raise ValidationError("O telefone deve conter apenas números.")

        return telefone

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError("Digite um endereço de email válido.")
        return email