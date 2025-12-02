#!/usr/bin/env python3
import re

file_path = "/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/brasilonlineassociacao-master/brasilonline/core/templates/index.html"

with open(file_path, 'r') as f:
    content = f.read()

#  First player fix
old_pattern1 = r'''{% if match\.result_set\.first\.player\.profile\.pin and
                                            match\.result_set\.first\.player\.first_name and
                                            match\.result_set\.first\.player\.last_name %}
                                            <a
                                                href="{% url 'profiles:publicprofile' pin=match\.result_set\.first\.player\.profile\.pin first=match\.result_set\.first\.player\.first_name last=match\.result_set\.first\.player\.last_name %}">{{
                                                match\.result_set\.first\.player\.first_name }} {{
                                                match\.result_set\.first\.player\.last_name }}</a>
                                            {% else %}
                                            {{ match\.result_set\.first\.player\.first_name }} {{
                                            match\.result_set\.first\.player\.last_name }}
                                            {% endif %}'''

new_pattern1 = '''{% if match.result_set.first.player.profile.pin and match.result_set.first.player.first_name and match.result_set.first.player.last_name %}
                                            <a href="{% url 'profiles:publicprofile' pin=match.result_set.first.player.profile.pin first=match.result_set.first.player.first_name last=match.result_set.first.player.last_name %}">{{ match.result_set.first.player.first_name }} {{ match.result_set.first.player.last_name }}</a>
                                            {% else %}
                                            {{ match.result_set.first.player.first_name }} {{ match.result_set.first.player.last_name }}
                                            {% endif %}'''

content = re.sub(old_pattern1, new_pattern1, content, flags=re.DOTALL)

# Second player fix
old_pattern2 = r'''{% if match\.result_set\.last\.player\.profile\.pin and
                                            match\.result_set\.last\.player\.first_name and
                                            match\.result_set\.last\.player\.last_name %}
                                            <a
                                                href="{% url 'profiles:publicprofile' pin=match\.result_set\.last\.player\.profile\.pin first=match\.result_set\.last\.player\.first_name last=match\.result_set\.last\.player\.last_name %}">{{
                                                match\.result_set\.last\.player\.first_name }} {{
                                                match\.result_set\.last\.player\.last_name }}</a>
                                            {% else %}
                                            {{ match\.result_set\.last\.player\.first_name }} {{
                                            match\.result_set\.last\.player\.last_name }}
                                            {% endif %}'''

new_pattern2 = '''{% if match.result_set.last.player.profile.pin and match.result_set.last.player.first_name and match.result_set.last.player.last_name %}
                                            <a href="{% url 'profiles:publicprofile' pin=match.result_set.last.player.profile.pin first=match.result_set.last.player.first_name last=match.result_set.last.player.last_name %}">{{ match.result_set.last.player.first_name }} {{ match.result_set.last.player.last_name }}</a>
                                            {% else %}
                                            {{ match.result_set.last.player.first_name }} {{ match.result_set.last.player.last_name }}
                                            {% endif %}'''

content = re.sub(old_pattern2, new_pattern2, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("Template fixed successfully!")
