"""Envio de e-mail do site.

Havia dois atalhos de envio iguais, um em `subscriptions/views.py` e outro em
`players/views.py`, e os dois colocavam a caixa da OBD como destinatária junto com o
usuário::

    "to": [from_, to]

O efeito era grave: o **link de redefinição de senha** e a **senha escolhida no
cadastro** iam parar junto com o remetente. Qualquer pessoa com acesso àquela caixa
conseguiria entrar na conta de qualquer jogador.

Agora a mensagem vai só para quem é dela, e a administração recebe um aviso separado
que não carrega nada capaz de dar acesso a uma conta.
"""
import logging

import resend
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _enviar(payload, descricao):
    """Envia e devolve a resposta do Resend, ou None se o envio falhar.

    **A exceção nunca sobe.** Um e-mail que não sai não pode derrubar a página que o
    disparou — no cadastro isso era grave: a conta já estava criada quando o envio
    acontecia, então uma falha aqui mostrava erro 500 para quem tinha acabado de se
    cadastrar com sucesso, e a pessoa tentava de novo e recebia "usuário já existe".

    A resposta é devolvida de propósito. A primeira versão desta função descartava o
    retorno, e por causa disso um diagnóstico de "os avisos não chegam" ficou cego:
    sem exceção e sem resposta, não havia como saber se o Resend tinha aceitado.
    """
    try:
        return resend.Emails.send(payload)
    except Exception:
        logger.exception('Falha ao enviar e-mail "%s" para %s', descricao, payload.get('to'))
        return None


def enviar_para_usuario(assunto, destinatario, template, contexto):
    """Envia a mensagem **apenas** para o destinatário.

    Nunca acrescente a caixa da administração aqui: é por este caminho que passam o
    link de redefinição de senha e a senha do cadastro.
    """
    return _enviar({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [destinatario],
        "subject": assunto,
        "text": render_to_string(template, contexto),
    }, assunto)


def avisar_administracao(assunto, corpo):
    """Avisa a administração de algo que aconteceu no site.

    Vai para `settings.EMAIL_AVISOS`, e **não** para o `DEFAULT_FROM_EMAIL`. Essa
    confusão já custou caro: o remetente é `noreply@`, que não tem caixa postal, e
    todos os avisos enviados para lá se perderam sem deixar rastro.

    O corpo tem que ser escrito à mão, curto, e **nunca** pode conter senha, link de
    redefinição ou qualquer outra coisa que sirva para entrar numa conta. Esse é o
    motivo de existir separado de :func:`enviar_para_usuario`, em vez de ser uma cópia
    da mensagem do usuário.
    """
    return _enviar({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [settings.EMAIL_AVISOS],
        "subject": assunto,
        "text": corpo,
    }, assunto)
