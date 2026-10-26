from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
import json
from .forms import OrcamentoPublicForm
from .models import Orcamento


def index(request):
    """Página inicial"""
    return render(request, 'learning_logs/index.html')


def sobre(request):
    """Página sobre"""
    return render(request, 'learning_logs/sobre.html')


def politica_privacidade(request):
    """Página de política de privacidade"""
    return render(request, 'learning_logs/politica_privacidade.html')


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
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'success': False, 'error': 'Dados inválidos.'}, status=400)

    form, error_response = _orcamento_form_from_data(data)
    if error_response:
        return error_response
    if not form.is_valid():
        return JsonResponse(
            {'success': False, 'error': 'Verifique os dados informados.', 'errors': form.errors.get_json_data()},
            status=400,
        )

    orcamento = form.save(commit=False)
    if request.user.is_authenticated:
        orcamento.user = request.user
    orcamento.save()
    return JsonResponse(
        {'success': True, 'message': 'Orçamento enviado com sucesso!'},
        status=201,
    )


def _orcamento_form_from_data(data):
    if not isinstance(data, dict):
        return None, JsonResponse({'success': False, 'error': 'Dados inválidos.'}, status=400)

    restricoes = data.get('restricoes', [])
    restricoes_validas = {'vegetariano', 'vegano', 'semlactose', 'alergia'}
    if (
        not isinstance(restricoes, list)
        or any(not isinstance(item, str) or item not in restricoes_validas for item in restricoes)
    ):
        return None, JsonResponse({'success': False, 'error': 'Restrições alimentares inválidas.'}, status=400)

    campos_texto = (
        'nome', 'telefone', 'tipoEvento', 'dataEvento', 'mensagem', 'rua',
        'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep',
    )
    if any(data.get(campo) is not None and not isinstance(data.get(campo), str) for campo in campos_texto):
        return None, JsonResponse({'success': False, 'error': 'Dados inválidos.'}, status=400)
    convidados = data.get('convidados')
    if isinstance(convidados, bool) or not isinstance(convidados, (int, str)):
        return None, JsonResponse({'success': False, 'error': 'Número de convidados inválido.'}, status=400)

    form_data = {
        'nome': data.get('nome'),
        'telefone': data.get('telefone'),
        'convidados': data.get('convidados'),
        'tipo_evento': data.get('tipoEvento'),
        'data_evento': data.get('dataEvento'),
        'restricoes': ','.join(restricoes),
        'mensagem': data.get('mensagem', ''),
        'rua': data.get('rua'),
        'numero': data.get('numero'),
        'complemento': data.get('complemento', ''),
        'bairro': data.get('bairro'),
        'cidade': data.get('cidade'),
        'estado': data.get('estado'),
        'cep': data.get('cep'),
    }
    return OrcamentoPublicForm(form_data), None


@login_required
@require_http_methods(["PATCH"])
def meus_orcamentos_update(request, id):
    """Atualiza um orçamento pertencente ao cliente autenticado."""
    orcamento = get_object_or_404(Orcamento, id=id, user=request.user)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'success': False, 'error': 'Dados inválidos.'}, status=400)

    form, error_response = _orcamento_form_from_data(data)
    if error_response:
        return error_response
    if not form.is_valid():
        return JsonResponse(
            {'success': False, 'error': 'Verifique os dados informados.', 'errors': form.errors.get_json_data()},
            status=400,
        )

    updated_orcamento = form.save(commit=False)
    for field in (
        'nome', 'telefone', 'convidados', 'tipo_evento', 'data_evento',
        'restricoes', 'mensagem', 'rua', 'numero', 'complemento',
        'bairro', 'cidade', 'estado', 'cep',
    ):
        setattr(orcamento, field, getattr(updated_orcamento, field))
    orcamento.save()
    return JsonResponse({'success': True, 'message': 'Orçamento atualizado com sucesso.'})


@login_required
@require_http_methods(["DELETE"])
def meus_orcamentos_delete(request, id):
    """Exclui um orçamento pertencente ao cliente autenticado."""
    orcamento = get_object_or_404(Orcamento, id=id, user=request.user)
    orcamento.delete()
    return JsonResponse({'success': True, 'message': 'Orçamento excluído com sucesso.'})


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

    return render(request, 'learning_logs/admin_dashboard_chef_edmilson.html', {
        'orcamentos_list': orcamentos_list,
    })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["PATCH"])
def orcamento_update_status(request, id):
    """Atualiza o status de um orçamento"""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

    novo_status = data.get('status')
    status_validos = {status for status, _ in Orcamento.STATUS_CHOICES}
    if not isinstance(novo_status, str) or novo_status not in status_validos:
        return JsonResponse({'success': False, 'error': 'Status inválido.'}, status=400)

    orcamento = get_object_or_404(Orcamento, id=id)
    orcamento.status = novo_status
    orcamento.save(update_fields=['status', 'data_atualizacao'])
    return JsonResponse({'success': True, 'message': 'Status atualizado'})


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