from django.db import models


class Assistida(models.Model):
    id_assistida = models.AutoField(primary_key=True)
    cpf_assistida = models.CharField(max_length=14, unique=True)
    nome_assistida = models.CharField(max_length=150)
    cep_assistida = models.CharField(max_length=8)
    idade_assistida = models.IntegerField()
    apelido_assistida = models.CharField(max_length=30, blank=True, null=True)
    cidade_assistida = models.CharField(max_length=30)
    estado_assistida = models.CharField(max_length=2)
    rua_assistida = models.CharField(max_length=50)
    num_endereco_assistida = models.IntegerField()
    complemento_endereco_assistida = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        db_table = 'Assistidas'
        verbose_name = 'Assistida'
        verbose_name_plural = 'Assistidas'
        ordering = ['nome_assistida']

    def __str__(self):
        return self.nome_assistida


class RegistroProntuario(models.Model):
    """
    Uma entrada do prontuário de uma assistida.

    O prontuário é o conjunto cronológico de registros escritos pelos
    profissionais (voluntários) que atenderam a assistida. Cada registro
    guarda quem escreveu e quando, o que preserva o histórico em vez de
    sobrescrever um único campo de texto.
    """
    id_registro = models.AutoField(primary_key=True)

    id_assistida = models.ForeignKey(
        Assistida,
        on_delete=models.CASCADE,
        db_column='id_assistida',
        related_name='registros_prontuario',
    )

    # PROTECT: não permite apagar um voluntário que já escreveu em prontuários.
    id_autor = models.ForeignKey(
        'voluntarios.Voluntario',
        on_delete=models.PROTECT,
        db_column='id_autor',
        related_name='registros_prontuario',
        verbose_name='Profissional',
    )

    texto = models.TextField(verbose_name='Registro')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'RegistrosProntuario'
        verbose_name = 'Registro de prontuário'
        verbose_name_plural = 'Registros de prontuário'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Prontuário de {self.id_assistida.nome_assistida} em {self.criado_em:%d/%m/%Y}"
