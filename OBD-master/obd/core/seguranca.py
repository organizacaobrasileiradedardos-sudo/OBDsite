"""Limite de tentativas de entrada no site.

Sem limite, descobrir uma senha fraca é só questão de insistir: nada impedia milhares de
tentativas seguidas, nem na tela dos jogadores nem na do admin do Django.

A contagem fica **no banco**, e não em memória, porque o Railway roda vários processos do
gunicorn. Um contador em memória seria por processo, e cada um deixaria passar o limite
inteiro — com quatro processos, quatro vezes mais tentativas do que o pretendido.

O ponto de captura é o sinal `user_login_failed`, que o Django dispara sempre que
`authenticate()` falha. Isso cobre de uma vez a tela dos jogadores (cujo formulário
chama `authenticate` na validação) e a do admin do Django, sem precisar mexer em nenhuma
das duas.
"""
import datetime

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

# Janela deslizante: o bloqueio se desfaz sozinho depois de alguns minutos sem tentativa.
JANELA = datetime.timedelta(minutes=15)

# Por nome de usuário: protege a conta de alguém que insiste numa senha só.
MAX_POR_USUARIO = 5

# Por endereço de origem: protege contra quem varre muitas contas de uma vez. É bem mais
# alto porque um clube inteiro pode estar atrás do mesmo endereço.
MAX_POR_IP = 20

# Falhas mais antigas que isto não servem para nada e são apagadas de tempos em tempos,
# para a tabela não crescer sem limite.
VALIDADE_DO_REGISTRO = datetime.timedelta(days=1)


def caminho_do_admin_login():
    """Endereço da tela de entrada do admin do Django.

    Descoberto pelo nome da rota, e não escrito à mão, porque o admin pode estar montado
    num endereço próprio (variável ADMIN_URL). Se ficasse fixo aqui, trocar o endereço
    faria o admin perder o limite de tentativas sem nenhum aviso.
    """
    try:
        return reverse('admin:login')
    except NoReverseMatch:
        return None


def caminhos_de_login():
    """Os endereços onde vale contar e barrar tentativas.

    Só estes. Assim, errar a senha na tela de "Atualizar Login" — que também chama
    `authenticate` — não tranca o jogador para fora do site.
    """
    caminhos = set()
    admin_login = caminho_do_admin_login()
    if admin_login:
        caminhos.add(admin_login)
    try:
        caminhos.add(reverse('players:login'))
    except NoReverseMatch:
        pass
    return caminhos


def ip_do_pedido(request):
    """Endereço de quem fez o pedido, considerando o proxy do Railway.

    Atrás de um proxy, `REMOTE_ADDR` é o próprio proxy e seria igual para todo mundo. O
    primeiro item de `X-Forwarded-For` é quem realmente fez o pedido.
    """
    encaminhado = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if encaminhado:
        return encaminhado.split(',')[0].strip()[:45]
    return (request.META.get('REMOTE_ADDR') or '')[:45]


def motivo_do_bloqueio(identificador, ip):
    """Por que esta tentativa deve ser barrada, ou None se pode seguir."""
    from obd.core.models import TentativaDeLogin

    recentes = TentativaDeLogin.objects.filter(criado_em__gte=timezone.now() - JANELA)

    if identificador and recentes.filter(identificador=identificador).count() >= MAX_POR_USUARIO:
        return 'usuario'
    if ip and recentes.filter(ip=ip).count() >= MAX_POR_IP:
        return 'ip'
    return None


@receiver(user_login_failed)
def registrar_falha(sender, credentials, request=None, **kwargs):
    """Anota uma tentativa que não deu certo."""
    if request is None or request.path not in caminhos_de_login():
        return

    from obd.core.models import TentativaDeLogin

    TentativaDeLogin.objects.create(
        identificador=(credentials.get('username') or '')[:150].strip().lower(),
        ip=ip_do_pedido(request),
    )
    TentativaDeLogin.objects.filter(
        criado_em__lt=timezone.now() - VALIDADE_DO_REGISTRO
    ).delete()


@receiver(user_logged_in)
def limpar_falhas(sender, user, request=None, **kwargs):
    """Entrou: as falhas daquele nome de usuário deixam de contar.

    As falhas do endereço continuam valendo — um acerto não deve zerar a contagem de
    quem estava varrendo várias contas a partir do mesmo lugar.
    """
    from obd.core.models import TentativaDeLogin

    TentativaDeLogin.objects.filter(identificador=user.get_username().strip().lower()).delete()
