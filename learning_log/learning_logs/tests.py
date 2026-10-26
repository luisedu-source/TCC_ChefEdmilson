import json
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Orcamento


class OrcamentoApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cliente', password='senha-teste')
        self.admin = User.objects.create_user(
            username='admin-teste',
            password='senha-teste',
            is_staff=True,
        )
        self.submit_url = reverse('learning_logs:orcamento_submit')

    def valid_payload(self):
        return {
            'nome': 'Cliente Teste',
            'telefone': '(15) 99999-0000',
            'convidados': 20,
            'tipoEvento': 'casamento',
            'dataEvento': (date.today() + timedelta(days=60)).isoformat(),
            'restricoes': ['vegetariano'],
            'mensagem': 'Sem amendoim.',
            'rua': 'Rua das Flores',
            'numero': '123',
            'complemento': '',
            'bairro': 'Centro',
            'cidade': 'Sorocaba',
            'estado': 'sp',
            'cep': '18000-000',
        }

    def create_orcamento(self, **overrides):
        data = {
            'user': self.user,
            'nome': 'Cliente Teste',
            'email': '',
            'telefone': '(15) 99999-0000',
            'convidados': 20,
            'tipo_evento': 'casamento',
            'data_evento': date.today() + timedelta(days=60),
            'restricoes': '',
            'mensagem': '',
            'rua': 'Rua das Flores',
            'numero': '123',
            'complemento': '',
            'bairro': 'Centro',
            'cidade': 'Sorocaba',
            'estado': 'SP',
            'cep': '18000-000',
        }
        data.update(overrides)
        return Orcamento.objects.create(**data)

    def test_submit_creates_valid_orcamento_for_logged_in_user(self):
        self.client.force_login(self.user)
        payload = self.valid_payload()
        payload['telefone'] = '15999790000'
        response = self.client.post(
            self.submit_url,
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        orcamento = Orcamento.objects.get()
        self.assertEqual(orcamento.user, self.user)
        self.assertEqual(orcamento.telefone, '(15) 99979-0000')
        self.assertEqual(orcamento.estado, 'SP')
        self.assertEqual(orcamento.restricoes, 'vegetariano')

    def test_submit_formats_landline_phone(self):
        payload = self.valid_payload()
        payload['telefone'] = '1532321234'
        response = self.client.post(
            self.submit_url,
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Orcamento.objects.get().telefone, '(15) 3232-1234')

    def test_submit_rejects_invalid_payloads_without_saving(self):
        payloads = [
            b'{invalid json',
            json.dumps(['not', 'an', 'object']),
            json.dumps({**self.valid_payload(), 'convidados': 0}),
            json.dumps({**self.valid_payload(), 'tipoEvento': 'unknown'}),
            json.dumps({**self.valid_payload(), 'restricoes': ['<script>']}),
            json.dumps({**self.valid_payload(), 'telefone': '123'}),
            json.dumps({**self.valid_payload(), 'nome': ['not', 'text']}),
            json.dumps({**self.valid_payload(), 'convidados': {}}),
        ]

        for payload in payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    self.submit_url,
                    data=payload,
                    content_type='application/json',
                )
                self.assertEqual(response.status_code, 400)
                self.assertFalse(response.json()['success'])

        self.assertEqual(Orcamento.objects.count(), 0)

    def test_customer_api_only_returns_the_authenticated_users_orcamentos(self):
        owned = self.create_orcamento()
        self.create_orcamento(nome='Outro cliente', user=self.admin)
        self.client.force_login(self.user)

        response = self.client.get(reverse('learning_logs:meus_orcamentos_api'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.json()['orcamentos']], [owned.id])

    def test_customer_can_update_owned_orcamento(self):
        orcamento = self.create_orcamento()
        self.client.force_login(self.user)

        response = self.client.patch(
            reverse('learning_logs:meus_orcamentos_update', args=[orcamento.id]),
            data=json.dumps(self.valid_payload()),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        orcamento.refresh_from_db()
        self.assertEqual(orcamento.nome, 'Cliente Teste')
        self.assertEqual(orcamento.estado, 'SP')
        self.assertEqual(orcamento.restricoes, 'vegetariano')
        self.assertEqual(orcamento.status, 'pendente')

    def test_customer_cannot_update_or_delete_another_users_orcamento(self):
        orcamento = self.create_orcamento(user=self.admin)
        self.client.force_login(self.user)

        update_response = self.client.patch(
            reverse('learning_logs:meus_orcamentos_update', args=[orcamento.id]),
            data=json.dumps(self.valid_payload()),
            content_type='application/json',
        )
        delete_response = self.client.delete(
            reverse('learning_logs:meus_orcamentos_delete', args=[orcamento.id]),
        )

        self.assertEqual(update_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.assertTrue(Orcamento.objects.filter(id=orcamento.id).exists())

    def test_customer_can_delete_owned_orcamento(self):
        orcamento = self.create_orcamento()
        self.client.force_login(self.user)

        response = self.client.delete(
            reverse('learning_logs:meus_orcamentos_delete', args=[orcamento.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Orcamento.objects.filter(id=orcamento.id).exists())

    def test_admin_status_api_rejects_malformed_payload_and_updates_valid_status(self):
        orcamento = self.create_orcamento()
        self.client.force_login(self.admin)
        url = reverse('learning_logs:orcamento_update_status', args=[orcamento.id])

        invalid_response = self.client.generic(
            'PATCH',
            url,
            data=json.dumps(['invalid']),
            content_type='application/json',
        )
        self.assertEqual(invalid_response.status_code, 400)

        invalid_status_response = self.client.generic(
            'PATCH',
            url,
            data=json.dumps({'status': []}),
            content_type='application/json',
        )
        self.assertEqual(invalid_status_response.status_code, 400)

        response = self.client.generic(
            'PATCH',
            url,
            data=json.dumps({'status': 'respondido'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        orcamento.refresh_from_db()
        self.assertEqual(orcamento.status, 'respondido')

    def test_admin_dashboard_serializes_customer_text_safely(self):
        self.create_orcamento(nome='<script>alert(1)</script>')
        self.client.force_login(self.admin)

        response = self.client.get(reverse('learning_logs:admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<script>alert(1)</script>')
