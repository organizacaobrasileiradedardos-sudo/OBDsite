"""Barra o envio do formulário de login quando já houve tentativas demais.

O sinal `user_login_failed` conta as falhas, mas contar não basta: é preciso recusar a
tentativa **antes** de verificar a senha. É o que este middleware faz, nos dois
endereços de login do site.
"""
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect

from obd.core.seguranca import (JANELA, caminho_do_admin_login, caminhos_de_login,
                                ip_do_pedido, motivo_do_bloqueio)

RECADO = (
    'Muitas tentativas de entrada seguidas. Por segurança, espere '
    f'{int(JANELA.total_seconds() // 60)} minutos sem tentar e depois tente de novo. '
    'Se você esqueceu a senha, use "Esqueci minha senha".'
)


class LimiteDeTentativasDeLogin:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            caminhos = caminhos_de_login()
            if request.path in caminhos:
                identificador = (request.POST.get('username') or '').strip().lower()
                if motivo_do_bloqueio(identificador, ip_do_pedido(request)):
                    return self._barrar(request)
        return self.get_response(request)

    def _barrar(self, request):
        # No admin do Django não há como devolver a mensagem pela tela de login do
        # site, então a resposta é direta. 429 é o código de "tentativas demais".
        if request.path == caminho_do_admin_login():
            return HttpResponse(RECADO, status=429, content_type='text/plain; charset=utf-8')

        messages.error(request, RECADO)
        return redirect(request.path)
