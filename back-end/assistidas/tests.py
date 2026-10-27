import json
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from voluntarios.models import Advogado, Voluntario
from .models import Assistida, RegistroProntuario

PAYLOAD = {
    'cpf': '12345678901', 'nome': 'Maria Teste', 'cep': '24020000', 'idade': 30,
    'apelido': 'Mari', 'cidade': 'Niterói', 'estado': 'RJ', 'rua': 'Rua A',
    'num_endereco': 10, 'complementoEndereco': 'ap 1',
}


def criar_assistida(**kw):
    dados = dict(
        cpf_assistida='111.111.111-11', nome_assistida='Maria da Silva', cep_assistida='24020000',
        idade_assistida=34, cidade_assistida='Niterói', estado_assistida='RJ',
        rua_assistida='Rua A', num_endereco_assistida=1)
    dados.update(kw)
    return Assistida.objects.create(**dados)


def criar_advogada(nome='Helena Advogada'):
    v = Voluntario.objects.create(
        email_voluntario='h@example.com', nomecompleto_voluntario=nome,
        datanasc_voluntario=date(1990, 1, 1), sexo_voluntario='F', cidade_voluntario='Niterói',
        estado_voluntario='RJ', endereco_voluntario='Rua B', telefone_voluntario='999990000',
        instagram_voluntario='@h', cpf_voluntario='000.000.000-01', rg_voluntario='123456789',
        cpfupload_voluntario=True, fotoupload_voluntario=True, termoupload_voluntario=True)
    Advogado.objects.create(id_voluntario=v, oab_advogado='RJ000001')
    return v


class ApiCadastroAssistidaTests(TestCase):
    url = '/api/assistidas/adicionar/'

    def post(self, payload):
        return self.client.post(self.url, json.dumps(payload), content_type='application/json')

    def test_cadastra_e_formata_cpf(self):
        r = self.post(PAYLOAD)
        self.assertEqual(r.status_code, 201)
        a = Assistida.objects.get(pk=r.json()['id'])
        self.assertEqual(a.cpf_assistida, '123.456.789-01')
        self.assertEqual(a.nome_assistida, 'Maria Teste')

    def test_cpf_duplicado_e_rejeitado(self):
        self.assertEqual(self.post(PAYLOAD).status_code, 201)
        self.assertEqual(self.post(PAYLOAD).status_code, 400)

    def test_get_nao_permitido(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_json_invalido(self):
        r = self.client.post(self.url, 'não é json', content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_rota_antiga_nao_existe_mais(self):
        self.assertEqual(self.client.post('/api/vitimas/adicionar/').status_code, 404)


# O storage de produção (Manifest) exige `collectstatic`; nos testes usamos o simples.
@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class PaginasPublicasTests(TestCase):
    def test_pagina_de_cadastro(self):
        r = self.client.get(reverse('cadastro_assistida'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id="cpf_assistida"')

    def test_url_antiga_redireciona(self):
        r = self.client.get('/cadastro-vitima/')
        self.assertRedirects(r, '/cadastro-assistida/', status_code=301)

    def test_home_continua_linkando_o_cadastro(self):
        self.assertContains(self.client.get('/'), '/cadastro-assistida/')


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class AreaInternaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.staff = U.objects.create_user('equipe', password='x', is_staff=True)
        cls.comum = U.objects.create_user('comum', password='x')
        cls.maria = criar_assistida()
        cls.joana = criar_assistida(cpf_assistida='222.222.222-22', nome_assistida='Joana Souza')
        cls.autora = criar_advogada()

    def test_anonimo_vai_para_login(self):
        for url in (reverse('assistidas_lista'), reverse('assistida_prontuario', args=[self.maria.pk])):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302)
            self.assertIn('/admin/login/', r['Location'])

    def test_usuario_sem_staff_nao_acessa(self):
        self.client.force_login(self.comum)
        r = self.client.get(reverse('assistidas_lista'))
        self.assertEqual(r.status_code, 302)

    def test_lista_e_busca(self):
        self.client.force_login(self.staff)
        r = self.client.get(reverse('assistidas_lista'))
        self.assertContains(r, 'Maria da Silva')
        self.assertContains(r, 'Joana Souza')
        r = self.client.get(reverse('assistidas_lista'), {'q': 'joana'})
        self.assertContains(r, 'Joana Souza')
        self.assertNotContains(r, 'Maria da Silva')
        r = self.client.get(reverse('assistidas_lista'), {'q': '111.111'})
        self.assertContains(r, 'Maria da Silva')

    def test_prontuario_mostra_autor_tipo_e_texto(self):
        RegistroProntuario.objects.create(id_assistida=self.maria, id_autor=self.autora, texto='Linha 1\nLinha 2')
        self.client.force_login(self.staff)
        r = self.client.get(reverse('assistida_prontuario', args=[self.maria.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Prontuário de Maria da Silva')
        self.assertContains(r, 'Helena Advogada')
        self.assertContains(r, 'Advogado(a)')
        self.assertContains(r, 'Linha 1<br>Linha 2')

    def test_prontuario_so_mostra_registros_da_propria_assistida(self):
        RegistroProntuario.objects.create(id_assistida=self.joana, id_autor=self.autora, texto='SEGREDO DA JOANA')
        self.client.force_login(self.staff)
        r = self.client.get(reverse('assistida_prontuario', args=[self.maria.pk]))
        self.assertNotContains(r, 'SEGREDO DA JOANA')
        self.assertContains(r, 'Ainda não há registros')

    def test_prontuario_escapa_html(self):
        RegistroProntuario.objects.create(
            id_assistida=self.maria, id_autor=self.autora, texto='<script>alert(1)</script>')
        self.client.force_login(self.staff)
        r = self.client.get(reverse('assistida_prontuario', args=[self.maria.pk]))
        self.assertNotContains(r, '<script>alert(1)</script>')
        self.assertContains(r, '&lt;script&gt;')

    def test_prontuario_inexistente_da_404(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('assistida_prontuario', args=[9999])).status_code, 404)

    def test_paginas_nao_ficam_em_cache(self):
        self.client.force_login(self.staff)
        r = self.client.get(reverse('assistida_prontuario', args=[self.maria.pk]))
        self.assertIn('no-store', r['Cache-Control'])

    def test_voluntario_com_registro_nao_pode_ser_apagado(self):
        from django.db.models import ProtectedError
        RegistroProntuario.objects.create(id_assistida=self.maria, id_autor=self.autora, texto='x')
        with self.assertRaises(ProtectedError):
            self.autora.delete()

    def test_admin_das_novas_telas_abre(self):
        U = get_user_model()
        U.objects.create_superuser('root', 'r@example.com', 'x')
        self.client.login(username='root', password='x')
        RegistroProntuario.objects.create(id_assistida=self.maria, id_autor=self.autora, texto='x')
        for nome in ('assistidas_assistida_changelist', 'assistidas_registroprontuario_changelist',
                     'voluntarios_voluntario_changelist', 'atendimentos_atendimento_changelist'):
            self.assertEqual(self.client.get(reverse(f'admin:{nome}')).status_code, 200, nome)
        self.assertEqual(
            self.client.get(reverse('admin:assistidas_assistida_change', args=[self.maria.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:assistidas_registroprontuario_add')).status_code, 200)
