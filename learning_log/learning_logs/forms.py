import re

from django import forms

from .models import Entry, Orcamento, Topic

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text': ''}

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': ''}
        widgets = {'text' : forms.Textarea(attrs={'cols' : 80})}


class OrcamentoPublicForm(forms.ModelForm):
    convidados = forms.IntegerField(min_value=1)

    class Meta:
        model = Orcamento
        fields = [
            'nome', 'telefone', 'convidados', 'tipo_evento', 'data_evento',
            'restricoes', 'mensagem', 'rua', 'numero', 'complemento',
            'bairro', 'cidade', 'estado', 'cep',
        ]

    def clean_telefone(self):
        telefone = self.cleaned_data['telefone']
        if len(re.sub(r'\D', '', telefone)) not in (10, 11):
            raise forms.ValidationError('Informe um telefone com DDD válido.')
        return telefone

    def clean_estado(self):
        return self.cleaned_data['estado'].strip().upper()

    def clean_cep(self):
        cep = self.cleaned_data['cep']
        if not re.fullmatch(r'\d{5}-?\d{3}', cep):
            raise forms.ValidationError('Informe um CEP válido.')
        return cep