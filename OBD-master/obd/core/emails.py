"""Envio de e-mail do site.

Havia dois atalhos de envio iguais, um em `subscriptions/views.py` e outro em
`players/views.py`, e os dois colocavam a caixa da OBD como destinatária junto com o
usuário::

    "to": [from_, to]

O efeito era grave: o **link de redefinição de senha** e a **senha escolhida no
cadastro** iam parar na caixa da OBD. Qualquer pessoa com acesso a ela conseguiria
entrar na conta de qualquer jogador.

Agora a mensagem vai só para quem é dela, e a administração recebe um aviso separado
que não carrega nada capaz de dar acesso a uma conta.
"""
import resend
from django.conf import settings
from django.template.loader import render_to_string


def enviar_para_usuario(assunto, destinatario, template, contexto):
    """Envia a mensagem **apenas** para o destinatário.

    Nunca acrescente a caixa da OBD aqui: é por este caminho que passam o link de
    redefinição de senha e a senha do cadastro.
    """
    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [destinatario],
        "subject": assunto,
        "text": render_to_string(template, contexto),
    })


def avisar_administracao(assunto, corpo):
    """Avisa a caixa da OBD de algo que aconteceu no site.

    O corpo tem que ser escrito à mão, curto, e **nunca** pode conter senha, link de
    redefinição ou qualquer outra coisa que sirva para entrar numa conta. Esse é o
    motivo de existir separado de :func:`enviar_para_usuario`, em vez de ser uma cópia
    da mensagem do usuário.
    """
    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [settings.DEFAULT_FROM_EMAIL],
        "subject": assunto,
        "text": corpo,
    })
