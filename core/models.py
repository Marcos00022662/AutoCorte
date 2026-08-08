from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    

    def __str__(self):
        return self.nome


class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    duracao = models.PositiveIntegerField()
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

    def __str__(self):
        return f"{self.cliente} - {self.data} {self.horario}"
