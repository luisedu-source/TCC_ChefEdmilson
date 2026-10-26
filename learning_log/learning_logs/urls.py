from django.urls import path
from . import views

app_name = 'learning_logs'

urlpatterns = [
    path('', views.index, name='index'),
    path('sobre/', views.sobre, name='sobre'),
    path('politica-de-privacidade/', views.politica_privacidade, name='politica_privacidade'),
    path('orcamento/', views.orcamento, name='orcamento'),
    path('orcamento/submit/', views.orcamento_submit, name='orcamento_submit'),
    path('meus-orcamentos/', views.meus_orcamentos, name='meus_orcamentos'),
    path('api/meus-orcamentos/', views.meus_orcamentos_api, name='meus_orcamentos_api'),
    path('api/meus-orcamentos/<int:id>/editar/', views.meus_orcamentos_update, name='meus_orcamentos_update'),
    path('api/meus-orcamentos/<int:id>/excluir/', views.meus_orcamentos_delete, name='meus_orcamentos_delete'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/orcamentos/<int:id>/', views.orcamento_update_status, name='orcamento_update_status'),
]