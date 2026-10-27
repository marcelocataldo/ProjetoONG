"""
Copia os cadastros da antiga tabela "Vitimas" (app `vitimas`) para "Assistidas".

- Se a tabela antiga não existir (banco novo), não faz nada.
- A tabela antiga NÃO é apagada: continua no banco como cópia de segurança.
  Depois de conferir os dados, ela pode ser removida manualmente.
"""
from django.core.management.color import no_style
from django.db import migrations

TABELA_ANTIGA = 'Vitimas'


def _formatar_cpf(cpf):
    digitos = ''.join(c for c in (cpf or '') if c.isdigit())
    if len(digitos) != 11:
        return cpf
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def copiar(apps, schema_editor):
    conn = schema_editor.connection
    if TABELA_ANTIGA not in conn.introspection.table_names():
        return

    Assistida = apps.get_model('assistidas', 'Assistida')

    with conn.cursor() as cursor:
        cursor.execute(
            f'SELECT id_vitima, cpf_vitima, nome_vitima, cep_vitima, idade_vitima, '
            f'apelido_vitima, cidade_vitima, estado_vitima, rua_vitima, '
            f'num_endereco_vitima, complemento_endereco_vitima FROM "{TABELA_ANTIGA}"'
        )
        linhas = cursor.fetchall()

    Assistida.objects.bulk_create([
        Assistida(
            id_assistida=l[0],
            cpf_assistida=_formatar_cpf(l[1]),
            nome_assistida=l[2],
            cep_assistida=l[3],
            idade_assistida=l[4],
            apelido_assistida=l[5],
            cidade_assistida=l[6],
            estado_assistida=l[7],
            rua_assistida=l[8],
            num_endereco_assistida=l[9],
            complemento_endereco_assistida=l[10],
        )
        for l in linhas
    ])

    # Como os ids foram inseridos explicitamente, realinha a sequência
    # (necessário no PostgreSQL; no SQLite a lista vem vazia).
    with conn.cursor() as cursor:
        for sql in conn.ops.sequence_reset_sql(no_style(), [Assistida]):
            cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('assistidas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copiar, migrations.RunPython.noop),
    ]
