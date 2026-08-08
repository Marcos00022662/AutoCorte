from django import forms

from .models import Agendamento, Cliente, Servico


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "telefone", "email"]


class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ["nome", "descricao", "preco", "duracao", "ativo"]


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
