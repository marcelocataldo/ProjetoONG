# Projeto ONG — Superação VD

Sistema web do Instituto Superação da Violência Doméstica: site institucional,
cadastro de **assistidas** e de **voluntários** (advogados, bacharéis e estagiários),
atendimentos e **prontuário** das assistidas.

Stack: Django 4.2 · Django REST Framework · SQLite (dev) / PostgreSQL (produção) · Docker · Railway.

## Rodar localmente (para testar)

```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                # Windows: copy .env.example .env

cd back-end
python manage.py migrate            # cria o banco local (SQLite)
python manage.py seed_dev           # dados fictícios + usuário de teste admin / admin
python manage.py runserver
```

Abra: <http://127.0.0.1:8000>

| O quê | Endereço |
|---|---|
| Site institucional | `/` |
| Formulário público de cadastro da assistida | `/cadastro-assistida/` |
| **Lista de assistidas** (só equipe) | `/assistidas/` |
| **Prontuário da assistida** (só equipe) | `/assistidas/<id>/prontuario/` |
| **Administração** (consultar/editar voluntários, assistidas, prontuários, atendimentos) | `/admin/` |
| API: cadastrar assistida (POST JSON) | `/api/assistidas/adicionar/` |
| API: cadastrar voluntário (POST JSON) | `/api/voluntarios/adicionar/{estagiario,advogado,bacharel}/` |

Sem dados de exemplo e com seu próprio usuário: `python manage.py createsuperuser`.

### Rodar os testes

```bash
cd back-end
python manage.py test
```

Rode sempre antes de enviar alterações. Se mudar algum model, gere a migration
(`python manage.py makemigrations`) — e confira com `python manage.py makemigrations --check`
que nada ficou pendente.

### Com Docker

```bash
docker compose up --build           # http://localhost:8000
docker compose exec web python manage.py seed_dev
```

## Prontuário

Cada assistida tem um prontuário formado por **registros** (`RegistroProntuario`):
texto livre + profissional que escreveu + data/hora. Novos registros são adicionados
em *Administração → Registros de prontuário* (ou pelo botão “+ Novo registro” na página
do prontuário). As páginas do prontuário exigem login de usuário da equipe (`is_staff`)
e não ficam em cache do navegador.

## Estrutura

```
back-end/
  server/        configurações e urls
  core/          páginas do site (templates/static) e comando seed_dev
  assistidas/    Assistida, RegistroProntuario, API e páginas internas
  voluntarios/   Voluntario, Estagiario, Advogado, Bacharel, Disponibilidade
  atendimentos/  Atendimento (API ainda em rascunho)
```

## Histórico de renomeação

O app `vitimas` virou `assistidas`. A migration `assistidas/0002` copia os dados da
antiga tabela `Vitimas` (se existir) para `Assistidas` e **mantém** a tabela antiga
no banco como backup. A URL `/cadastro-vitima/` redireciona para `/cadastro-assistida/`.
