import secrets

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
    data = models.DateField()
    horario = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente",
    )
    token = models.CharField(max_length=32, unique=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(16)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente} - {self.data} {self.horario}"

    def clean(self):
        if self.status == "cancelado":
            return

        conflito = Agendamento.objects.filter(
            data=self.data,
            horario=self.horario,
        ).exclude(status="cancelado")
        if self.pk:
            conflito = conflito.exclude(pk=self.pk)
        if conflito.exists():
            raise ValidationError({"horario": "Este horário acabou de ser reservado. Escolha outro."})