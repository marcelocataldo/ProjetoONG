import json

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from services import formatar_cpf
from .models import Assistida


# ---------------------------------------------------------------- API pública
@csrf_exempt
def adicionar(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        }, status=405)

    try:
        data = json.loads(request.body)

        assistida = Assistida.objects.create(
            cpf_assistida=formatar_cpf(data.get('cpf')),
            nome_assistida=data.get('nome'),
            cep_assistida=data.get('cep'),
            idade_assistida=data.get('idade'),
            apelido_assistida=data.get('apelido'),
            cidade_assistida=data.get('cidade'),
            estado_assistida=data.get('estado'),
            rua_assistida=data.get('rua'),
            num_endereco_assistida=data.get('num_endereco'),
            complemento_endereco_assistida=data.get('complementoEndereco'),
        )

        return JsonResponse({
            'success': True,
            'message': 'Assistida cadastrada com sucesso!',
            'id': assistida.id_assistida
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao cadastrar: {str(e)}'
        }, status=400)


# ------------------------------------------- Páginas internas (só equipe/staff)
@never_cache
@staff_member_required
def lista(request):
    busca = request.GET.get('q', '').strip()
    assistidas = Assistida.objects.annotate(
        total_registros=Count('registros_prontuario')
    )
    if busca:
        assistidas = assistidas.filter(
            Q(nome_assistida__icontains=busca)
            | Q(cpf_assistida__icontains=busca)
            | Q(apelido_assistida__icontains=busca)
        )
    return render(request, 'assistidas/lista.html', {
        'assistidas': assistidas,
        'busca': busca,
    })


@never_cache
@staff_member_required
def prontuario(request, id_assistida):
    assistida = get_object_or_404(Assistida, pk=id_assistida)
    registros = assistida.registros_prontuario.select_related(
        'id_autor',
        'id_autor__estagiario',
        'id_autor__advogado',
        'id_autor__bacharel',
    )
    return render(request, 'assistidas/prontuario.html', {
        'assistida': assistida,
        'registros': registros,
    })
