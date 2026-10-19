import json

from django.test import TestCase

from voluntarios.models import Estagiario, Voluntario

BASE = {
    'email': 'c@example.com', 'nome': 'Carlos Teste', 'dataNascimento': '2000-03-10', 'sexo': 'M',
    'cidade': 'Niterói', 'estado': 'RJ', 'endereco': 'Rua C, 5', 'telefone': '999990000',
    'instagram': '@c', 'cpf': '98765432100', 'rg': '123456789',
    'cpfupload': True, 'fotoupload': True, 'termoupload': True,
}


class ApiVoluntariosTests(TestCase):
    def test_cadastra_estagiario(self):
        r = self.client.post('/api/voluntarios/adicionar/estagiario/',
                             json.dumps({**BASE, 'curso': 'Direito', 'periodo': '5'}),
                             content_type='application/json')
        self.assertEqual(r.status_code, 201, r.content)
        v = Voluntario.objects.get(pk=r.json()['id'])
        self.assertEqual(v.cpf_voluntario, '987.654.321-00')
        self.assertEqual(Estagiario.objects.get(id_voluntario=v).periodo_estagiario, '5')
        self.assertEqual(v.tipo, 'Estagiário(a)')

    def test_get_nao_permitido(self):
        self.assertEqual(self.client.get('/api/voluntarios/adicionar/estagiario/').status_code, 405)
