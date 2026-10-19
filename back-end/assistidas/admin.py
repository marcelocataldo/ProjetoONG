from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Assistida, RegistroProntuario


class RegistroProntuarioInline(admin.StackedInline):
    model = RegistroProntuario
    extra = 0
    fields = ['id_autor', 'texto', 'criado_em']
    readonly_fields = ['criado_em']
    show_change_link = True


@admin.register(Assistida)
class AssistidaAdmin(admin.ModelAdmin):
    list_display = [
        'id_assistida',
        'nome_assistida',
        'cpf_assistida',
        'idade_assistida',
        'cidade_assistida',
        'estado_assistida',
        'link_prontuario',
    ]
    list_filter = ['estado_assistida', 'cidade_assistida']
    search_fields = ['nome_assistida', 'cpf_assistida', 'apelido_assistida']
    readonly_fields = ['id_assistida']
    list_per_page = 25
    inlines = [RegistroProntuarioInline]

    fieldsets = (
        ('Informações Pessoais', {
            'fields': (
                'id_assistida',
                'nome_assistida',
                'cpf_assistida',
                'idade_assistida',
                'apelido_assistida',
            )
        }),
        ('Endereço', {
            'fields': (
                'cep_assistida',
                'rua_assistida',
                'num_endereco_assistida',
                'complemento_endereco_assistida',
                'cidade_assistida',
                'estado_assistida',
            )
        }),
    )

    @admin.display(description='Prontuário')
    def link_prontuario(self, obj):
        url = reverse('assistida_prontuario', args=[obj.pk])
        total = obj.registros_prontuario.count()
        return format_html('<a href="{}">Abrir ({})</a>', url, total)


@admin.register(RegistroProntuario)
class RegistroProntuarioAdmin(admin.ModelAdmin):
    list_display = ['id_registro', 'id_assistida', 'id_autor', 'criado_em']
    list_filter = ['criado_em']
    search_fields = [
        'id_assistida__nome_assistida',
        'id_autor__nomecompleto_voluntario',
        'texto',
    ]
    autocomplete_fields = ['id_assistida', 'id_autor']
    readonly_fields = ['criado_em', 'atualizado_em']
    date_hierarchy = 'criado_em'
