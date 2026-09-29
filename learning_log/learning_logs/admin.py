from django.contrib import admin
from learning_logs.models import Topic, Entry, Orcamento

admin.site.register(Topic)
admin.site.register(Entry)

@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'tipo_evento', 'data_evento', 'status', 'data_criacao')
    list_filter = ('status', 'tipo_evento', 'data_criacao')
    search_fields = ('nome', 'email', 'telefone')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'email', 'telefone', 'convidados')
        }),
        ('Detalhes do Evento', {
            'fields': ('tipo_evento', 'data_evento', 'restricoes', 'mensagem')
        }),
        ('Endereço', {
            'fields': ('rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep')
        }),
        ('Controle', {
            'fields': ('status', 'data_criacao', 'data_atualizacao')
        }),
    )
