import secrets
from datetime import datetime, timedelta

from django.db import models
from django.core.exceptions import ValidationError


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nome


class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    duracao = models.PositiveIntegerField()
    foto = models.ImageField(upload_to="servicos/", blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Agendamento(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("confirmado", "Confirmado"),
        ("cancelado", "Cancelado"),
        ("concluido", "Concluído"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    data = models.DateField()
    horario = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente",
    )
    token = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(16)

        if self._state.adding and self.servico_id:
            self.preco = self.servico.preco

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente} - {self.data} {self.horario}"

    @property
    def intervalo(self):
        """Retorna (inicio, fim) desse agendamento como datetimes,
        considerando a duração do serviço escolhido."""
        inicio = datetime.combine(self.data, self.horario)
        fim = inicio + timedelta(minutes=self.servico.duracao)
        return inicio, fim

    def clean(self):
        if self.status == "cancelado":
            return

        # Sem esses três campos não dá pra calcular o intervalo,
        # então deixa outras validações (obrigatoriedade) cuidarem
        # disso.
        if not (self.data and self.horario and self.servico_id):
            return

        inicio, fim = self.intervalo

        candidatos = (
            Agendamento.objects
            .filter(data=self.data)
            .exclude(status="cancelado")
            .select_related("servico")
        )

        if self.pk:
            candidatos = candidatos.exclude(pk=self.pk)

        for candidato in candidatos:
            inicio_c, fim_c = candidato.intervalo

            # Dois intervalos se sobrepõem se um começa antes do
            # outro terminar, nos dois sentidos.
            if inicio < fim_c and fim > inicio_c:
                raise ValidationError({
                    "horario": (
                        "Este horário conflita com outro agendamento "
                        "já existente. Escolha outro."
                    )
                })

