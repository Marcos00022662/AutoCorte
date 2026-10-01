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

class ReagendamentoForm(forms.ModelForm):
    novo_horario = forms.ChoiceField(
        choices=(),
    )
    nova_data = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "js-date-picker",
                "autocomplete": "off",
                "placeholder": "aaaa-mm-dd",
                "type": "text",
            },
            format="%Y-%m-%d",
        )
    )

    class Meta:
        model = Agendamento
        fields = ["novo_horario", "nova_data"]
    
    def __init__(self, *args, horarios_disponiveis=None, **kwargs):
        super().__init__(*args, **kwargs)
        horarios_disponiveis = horarios_disponiveis or []
        self.horarios_validos = set(horarios_disponiveis)
        self.fields["novo_horario"].choices = [
        (horario, horario) for horario in horarios_disponiveis]
        
    def clean_nova_data(self):
        nova_data = self.cleaned_data.get("nova_data")

        if nova_data < date.today():
            raise ValidationError("Escolha uma data futura.")

        return nova_data

    def clean_novo_horario(self):
        novo_horario = self.cleaned_data.get("novo_horario")

        if novo_horario:
            try:
                datetime.datetime.strptime(novo_horario, "%H:%M")
            except ValueError:
                raise ValidationError("Escolha um horário válido.")

            if self.horarios_validos and novo_horario not in self.horarios_validos:
                raise ValidationError(
                    "Este horário não está mais disponível. Escolha outro."
                )

        return novo_horario
    

class AgendamentoClienteForm(forms.ModelForm):

    nome = forms.CharField(max_length=100)
    telefone = forms.CharField(max_length=20)
    email = forms.EmailField(required=False)

    horario = forms.ChoiceField(
        choices=(),
        widget=forms.Select(attrs={"class": "js-time-picker"})
    )

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

    def __init__(
        self,
        *args,
        horarios_disponiveis=None,
        **kwargs
    ):
        # Listagem de horários do formulário
        super().__init__(*args, **kwargs)

        self.fields["servico"].queryset = Servico.objects.filter(
            ativo=True
        )

        horarios_disponiveis = horarios_disponiveis or []

        # Guardamos o conjunto de horários válidos para validar
        # depois em clean_horario (evita que alguém envie um
        # horário que não estava entre os disponíveis).
        self._horarios_validos = set(horarios_disponiveis)

        # Aviso (não bloqueante) preenchido em clean_telefone()
        # quando o telefone já existe cadastrado com outro nome.
        self.aviso_telefone = None

        self.fields["horario"].choices = [
            (horario, horario)
            for horario in horarios_disponiveis
        ]

    # Validação do horário
    def clean_horario(self):

        horario = self.cleaned_data.get("horario")

        if horario:
            try:
                datetime.datetime.strptime(
                    horario,
                    "%H:%M"
                )
            except ValueError:
                raise ValidationError(
                    "Escolha um horário válido."
                )

            if (
                self._horarios_validos
                and horario not in self._horarios_validos
            ):
                raise ValidationError(
                    "Este horário não está mais disponível. "
                    "Escolha outro."
                )

        return horario

    # Validação da data
    def clean_data(self):

        data_atendimento = self.cleaned_data["data"]

        if data_atendimento < date.today():
            raise ValidationError(
                "Escolha uma data futura."
            )

        return data_atendimento

    # Validação do nome
    def clean_nome(self):

        nome = self.cleaned_data.get("nome", "").strip()

        if len(nome) < 3:
            raise ValidationError(
                "O nome deve ter pelo menos 3 caracteres."
            )

        return nome

    # Validação do telefone
    def clean_telefone(self):

        telefone = (
            self.cleaned_data
            .get("telefone", "")
            .strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
            .replace("+", "")
        )

        # Remove o DDI 55 caso o cliente já tenha digitado com ele
        # (ex.: "5511999999999"), para manter só DDD + número.
        if len(telefone) in (12, 13) and telefone.startswith("55"):
            telefone = telefone[2:]

        if telefone == "":
            raise ValidationError(
                "O telefone é obrigatório."
            )

        if not telefone.isdigit():
            raise ValidationError(
                "O telefone deve conter apenas números."
            )

        if len(telefone) not in (10, 11):
            raise ValidationError(
                "O telefone deve ter 10 ou 11 dígitos."
            )

        # Verifica se esse telefone já pertence a outro cliente
        # cadastrado com um nome diferente. Aqui NÃO bloqueamos o
        # envio — apenas guardamos um aviso em self.aviso_telefone,
        # que a view pode exibir para o usuário (ex.: via
        # django.contrib.messages) depois que o form for salvo.
        # OBS: "nome" já foi validado em clean_nome() antes de
        # chegar aqui, pois é declarado antes de "telefone" na
        # classe (a ordem de limpeza dos campos segue a ordem de
        # declaração).
        nome = self.cleaned_data.get("nome", "").strip()

        if nome:
            cliente_existente = (
                Cliente.objects
                .filter(telefone=telefone)
                .exclude(nome__iexact=nome)
                .first()
            )

            if cliente_existente:
                self.aviso_telefone = (
                    f"Encontramos esse telefone já cadastrado como "
                    f"\"{cliente_existente.nome}\". Mantivemos o "
                    f"nome original no cadastro."
                )

        return telefone

    # Validação do email
    def clean_email(self):

        email = self.cleaned_data.get(
            "email",
            ""
        ).strip()

        if email and not re.match(
            r"[^@]+@[^@]+\.[^@]+",
            email
        ):
            raise ValidationError(
                "Digite um endereço de email válido."
            )

        return email

    # Validações gerais do formulário
    def clean(self):

        cleaned_data = super().clean()

        data_atendimento = cleaned_data.get("data")
        horario_atendimento = cleaned_data.get("horario")

        # Verifica se a data já passou
        if data_atendimento and data_atendimento < date.today():
            raise ValidationError(
                "Escolha uma data futura."
            )

        # Verifica se, mesmo sendo hoje, o horário escolhido já
        # passou (ex.: a página ficou aberta e o horário que era
        # válido no carregamento já não é mais).
        if (
            data_atendimento
            and horario_atendimento
            and data_atendimento == date.today()
        ):
            hora, minuto = (
                int(parte) for parte in horario_atendimento.split(":")
            )
            horario_completo = datetime.datetime.combine(
                data_atendimento,
                datetime.time(hour=hora, minute=minuto),
            )

            if horario_completo <= datetime.datetime.now():
                raise ValidationError(
                    "Esse horário já passou. Escolha outro."
                )

    
        servico = cleaned_data.get("servico")

        if data_atendimento and horario_atendimento and servico:
            hora, minuto = (
                int(parte) for parte in horario_atendimento.split(":")
            )
            inicio_novo = datetime.datetime.combine(
                data_atendimento,
                datetime.time(hour=hora, minute=minuto),
            )
            fim_novo = inicio_novo + datetime.timedelta(
                minutes=servico.duracao
            )

            candidatos = (
                Agendamento.objects
                .filter(data=data_atendimento)
                .exclude(status="cancelado")
                .select_related("servico")
            )

            for candidato in candidatos:
                inicio_existente = datetime.datetime.combine(
                    candidato.data, candidato.horario
                )
                fim_existente = inicio_existente + datetime.timedelta(
                    minutes=candidato.servico.duracao
                )

                if inicio_novo < fim_existente and fim_novo > inicio_existente:
                    raise ValidationError(
                        "Este horário conflita com outro agendamento "
                        "já existente. Escolha outro."
                    )

        return cleaned_data

      