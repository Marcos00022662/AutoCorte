from django.test import TestCase
from core.models import Cliente, Servico, Agendamento
from datetime import date, time 
from django.core.exceptions import ValidationError
from core.forms import ReagendamentoForm
# Creat e your tests here.
class TesteAgenda(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nome="Cliente Teste",
            telefone="123456789",
            email='cliente@teste.com')
        
        self.servico = Servico.objects.create(
            nome="Serviço Teste",
            descricao="Descrição do serviço teste",
            preco=100.00,
            duracao=60,
        )
        
        self.servico_curto = Servico.objects.create(
            nome="Serviço Curto",
            descricao="Serviço de 30 minutos",
            preco=50.00,
            duracao=30,
        )

        self.agendamento = Agendamento.objects.create(
            cliente=self.cliente, 
            servico=self.servico,
            data= date(2026, 10, 30),
            horario=time(10, 0),
            status="pendente"
        )
    def test_conflito_de_horario(self):
        segundo_agendamento = Agendamento(
            cliente=self.cliente,
            servico=self.servico,
            data="2026-10-30",
            horario="10:30:00",
            status="pendente"
    )

        with self.assertRaises(ValidationError):
            segundo_agendamento.full_clean()

    def test_horario_sem_conflito(self):
        segundo_agendamento = Agendamento(
            cliente=self.cliente,
            servico=self.servico,
            data= date(2026, 10, 30),
            horario="11:00:00",
            status="pendente"
        )

        segundo_agendamento.full_clean()

    def test_conflito_com_duracao_diferente(self):
        segundo_agendamento = Agendamento(
            cliente=self.cliente,
            servico=self.servico_curto,
            data= date(2026, 10, 30),
            horario="10:45:00",
            status="pendente"
        )

        with self.assertRaises(ValidationError):
            segundo_agendamento.full_clean()

    def test_preco_historico(self):
        self.assertEqual(self.agendamento.preco, 100.00)
        self.servico.preco = 150.00
        self.servico.save()
        self.assertEqual(self.agendamento.preco, 100.00)

    def test_agendamento_cancelado_nao_bloqueia_horario(self):
        self.agendamento.status = "cancelado"
        self.agendamento.save()

        segundo_agendamento = Agendamento(
            cliente=self.cliente,
            servico=self.servico,
            data=date(2026, 10, 30),
            horario="10:30:00",
            status="pendente"
        )

        segundo_agendamento.full_clean()

    def test_reagendamento(self):
        self.agendamento.status = "cancelado"
        self.agendamento.save()

        self.agendamento.data = date(2026, 10, 31)
        self.agendamento.horario = "11:00:00"
        self.agendamento.status = "pendente"
        self.agendamento.save()

        self.assertEqual(self.agendamento.data, date(2026, 10, 31))
        self.assertEqual(self.agendamento.horario, "11:00:00")

    def test_reagendamento_com_conflito(self):
        segundo_agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            servico=self.servico_curto,
            data=date(2026, 10, 31),
            horario="11:00:00",
            status="pendente"
        )

        self.agendamento.status = "cancelado"
        self.agendamento.save()

        self.agendamento.data = date(2026, 10, 31)
        self.agendamento.horario = "11:00:00"
        self.agendamento.status = "pendente"

        with self.assertRaises(ValidationError):
            self.agendamento.full_clean()

    def test_formulario_reagendamento_valido(self):
        formulario = ReagendamentoForm(
            data={
                "novo_horario": "14:00",
                "nova_data": "2026-11-02",
            },
            horarios_disponiveis=["10:00", "11:00", "14:00", "15:00"],
            instance=self.agendamento,
        )

        self.assertTrue(formulario.is_valid())
    def test_reagendamento_com_data_passada(self):
        formulario = ReagendamentoForm(
            data={
                "novo_horario": "14:00",
                "nova_data": "2020-01-01",
            },
            horarios_disponiveis=["14:00"],
            instance=self.agendamento,
        )

        self.assertFalse(formulario.is_valid())
        self.assertIn("nova_data", formulario.errors)

    def test_reagendamento_com_horario_indisponivel(self):
        formulario = ReagendamentoForm(
            data={
                "novo_horario": "13:00",
                "nova_data": "2026-11-02",
            },
            horarios_disponiveis=["10:00", "11:00", "14:00", "15:00"],
            instance=self.agendamento,
        )

        self.assertFalse(formulario.is_valid())
        self.assertIn("novo_horario", formulario.errors)