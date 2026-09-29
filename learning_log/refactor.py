# -*- coding: utf-8 -*-
import sys

with open(r'learning_logs\templates\learning_logs\orcamento.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = [
    '{% extends \"base.html\" %}\n',
    '{% load static %}\n',
    '\n',
    '{% block title %}Chef Edmilson - Solicitar Orçamento{% endblock %}\n',
    '\n',
    '{% block content %}\n',
    '<style>\n'
]

# Extract styles starting from line 38 (skipping header overrides) up to </style>
style_start = 38
style_end = 0
for i, line in enumerate(lines):
    if '</style>' in line:
        style_end = i
        break

new_lines.extend(lines[style_start:style_end+1])

# Extract everything from <main to the end, but excluding </body> and </html>
main_start = 0
for i, line in enumerate(lines):
    if '<main class=\"orcamento-container\">' in line:
        main_start = i
        break

main_end = len(lines)
for i in range(len(lines)-1, -1, -1):
    if '</body>' in lines[i]:
        main_end = i
        break

new_lines.extend(lines[main_start:main_end])
new_lines.append('{% endblock %}\n')

with open(r'learning_logs\templates\learning_logs\orcamento.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Rewrite successful.')
