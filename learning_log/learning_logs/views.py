from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
import json
from .models import Orcamento


def index(request):
    """Página inicial"""
    return render(request, 'learning_logs/index.html')


def sobre(request):
    """Página sobre"""
    return render(request, 'learning_logs/sobre.html')


def orcamento(request):
    """Página de orçamento"""
    return render(request, 'learning_logs/orcamento.html')


def cadastro(request):
    """Página de cadastro"""
    return render(request, 'learning_logs/cadastro.html')


@require_http_methods(["POST"])
def orcamento_submit(request):
    """Recebe dados do formulário de orçamento via AJAX"""
    try:
        data = json.loads(request.body)

        # Validação mínima dos campos obrigatórios
        campos_obrigatorios = ['nome', 'telefone', 'convidados',
                               'tipoEvento', 'dataEvento', 'rua', 'numero',
                               'bairro', 'cidade', 'estado', 'cep']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return JsonResponse(
                    {'success': False, 'error': f'Campo obrigatório ausente: {campo}'},
                    status=400
                )

        orcamento = Orcamento.objects.create(
            user=request.user if request.user.is_authenticated else None,
            nome=data.get('nome', ''),
            email='',
            telefone=data.get('telefone', ''),
            convidados=int(data.get('convidados', 0)),
            tipo_evento=data.get('tipoEvento', ''),
            data_evento=data.get('dataEvento', ''),
            restricoes=','.join(data.get('restricoes', [])),
            mensagem=data.get('mensagem', ''),
            rua=data.get('rua', ''),
            numero=data.get('numero', ''),
            complemento=data.get('complemento', ''),
            bairro=data.get('bairro', ''),
            cidade=data.get('cidade', ''),
            estado=data.get('estado', ''),
            cep=data.get('cep', ''),
        )

        return JsonResponse({'success': True, 'message': 'Orçamento enviado com sucesso!'})

    except (ValueError, TypeError) as e:
        return JsonResponse({'success': False, 'error': 'Número de convidados inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def is_admin(user):
    """Verifica se o usuário é administrador"""
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Painel de administração com lista de orçamentos"""
    orcamentos = Orcamento.objects.all().order_by('-id').values(
        'id', 'nome', 'email', 'telefone', 'convidados', 'tipo_evento',
        'data_evento', 'rua', 'numero', 'complemento', 'bairro',
        'cidade', 'estado', 'cep', 'restricoes', 'mensagem', 'status'
    )

    # Converter datas para string (date objects não são serializáveis por json.dumps)
    orcamentos_list = []
    for o in orcamentos:
        o_dict = dict(o)
        if o_dict.get('data_evento'):
            o_dict['data_evento'] = str(o_dict['data_evento'])  # "YYYY-MM-DD"
        orcamentos_list.append(o_dict)

    orcamentos_json = json.dumps(orcamentos_list)

    return render(request, 'learning_logs/admin_dashboard_chef_edmilson.html', {
        'orcamentos_json': orcamentos_json,
    })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["PATCH"])
def orcamento_update_status(request, id):
    """Atualiza o status de um orçamento"""
    try:
        data = json.loads(request.body)
        novo_status = data.get('status', '')

        STATUS_VALIDOS = ['pendente', 'respondido', 'recusado']
        if novo_status not in STATUS_VALIDOS:
            return JsonResponse(
                {'success': False, 'error': f'Status inválido. Use: {", ".join(STATUS_VALIDOS)}'},
                status=400
            )

        orcamento = Orcamento.objects.get(id=id)
        orcamento.status = novo_status
        orcamento.save()

        return JsonResponse({'success': True, 'message': 'Status atualizado'})

    except Orcamento.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Orçamento não encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def meus_orcamentos(request):
    """Página onde o cliente pode ver seus orçamentos"""
    orcamentos = Orcamento.objects.filter(
        user=request.user
    ).order_by('-data_criacao')
    
    return render(request, 'learning_logs/meus_orcamentos.html', {
        'orcamentos': orcamentos,
    })


@login_required
@require_http_methods(["GET"])
def meus_orcamentos_api(request):
    """API para obter orçamentos do cliente logado"""
    orcamentos = Orcamento.objects.filter(
        user=request.user
    ).order_by('-data_criacao').values(
        'id', 'nome', 'email', 'telefone', 'convidados', 'tipo_evento',
        'data_evento', 'rua', 'numero', 'complemento', 'bairro',
        'cidade', 'estado', 'cep', 'restricoes', 'mensagem', 'status',
        'data_criacao', 'data_atualizacao'
    )
    
    orcamentos_list = []
    for o in orcamentos:
        o_dict = dict(o)
        if o_dict.get('data_evento'):
            o_dict['data_evento'] = str(o_dict['data_evento'])
        if o_dict.get('data_criacao'):
            o_dict['data_criacao'] = o_dict['data_criacao'].isoformat()
        if o_dict.get('data_atualizacao'):
            o_dict['data_atualizacao'] = o_dict['data_atualizacao'].isoformat()
        orcamentos_list.append(o_dict)
    
    return JsonResponse({'orcamentos': orcamentos_list})