from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class Topic(models.Model):
    """Um assunto sobre qual o usuario esta aprendendo"""
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Devolve uma representaçao em string do modelo"""
        return self.text

class Entry(models.Model):
    """Algo especifico aprendido sobre um assunto"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        """Devolve uma representaçao em string do modelo"""

        return self.text[:50] + '...'

class Orcamento(models.Model):
    """Solicitação de orçamento de um cliente"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('respondido', 'Respondido'),
        ('recusado', 'Recusado'),
    ]
    
    TIPO_EVENTO_CHOICES = [
        ('casamento', 'Casamento'),
        ('aniversario', 'Aniversário'),
        ('corporativo', 'Evento Corporativo'),
        ('formatura', 'Formatura'),
        ('inaugural', 'Festa de Inauguração'),
        ('outro', 'Outro'),
    ]
    
    # Informações básicas
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos')
    nome = models.CharField(max_length=150)
    email = models.EmailField(blank=True, default='')
    telefone = models.CharField(max_length=20)
    convidados = models.IntegerField()
    
    # Detalhes do evento
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    data_evento = models.DateField()
    
    # Preferências
    restricoes = models.CharField(max_length=500, blank=True)
    mensagem = models.TextField(blank=True)
    
    # Endereço
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)
    
    # Controle
    protocolo = models.CharField(max_length=20, unique=True, blank=True, null=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name_plural = 'Orçamentos'
    
    def save(self, *args, **kwargs):
        """Gera automaticamente o protocolo se não existir"""
        if not self.protocolo:
            # Formato: ORC-20261008-XXXX (onde X são dígitos aleatórios/ID)
            data_str = timezone.now().strftime('%Y%m%d')
            # Usar UUID curto (primeiros 8 caracteres) para garantir unicidade
            uuid_short = str(uuid.uuid4()).split('-')[0].upper()
            self.protocolo = f"ORC-{data_str}-{uuid_short}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.protocolo} - {self.nome} - {self.tipo_evento} ({self.status})"