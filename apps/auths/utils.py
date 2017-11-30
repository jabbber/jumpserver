# ~*~ coding: utf-8 ~*~
#
import logging
import requests
import ipaddress
import base64
import uuid

from django.core.cache import cache
from django.conf import settings
from django.utils.translation import ugettext as _

from common.tasks import send_mail_async
from common.utils import reverse
from .models import LoginLog


logger = logging.getLogger('jumpserver')
DEFAULT_CACHE_TIME = 3600


def send_reset_password_mail(user):
    subject = _('Reset password')
    recipient_list = [user.email]
    message = _("""
    Hello %(name)s:
    </br>
    Please click the link below to reset your password, if not your request, concern your account security
    </br>
    <a href="%(rest_password_url)s?token=%(rest_password_token)s">Click here reset password</a>
    </br>
    This link is valid for 1 hour. After it expires, <a href="%(forget_password_url)s?email=%(email)s">request new one</a>

    </br>
    ---

    </br>
    <a href="%(login_url)s">Login direct</a>

    </br>
    """) % {
        'name': user.name,
        'rest_password_url': reverse('users:reset-password', external=True),
        'rest_password_token': user.generate_reset_token(),
        'forget_password_url': reverse('users:forgot-password', external=True),
        'email': user.email,
        'login_url': reverse('users:login', external=True),
    }
    if settings.DEBUG:
        logger.debug(message)

    send_mail_async.delay(subject, message, recipient_list, html_message=message)


def send_reset_ssh_key_mail(user):
    subject = _('SSH Key Reset')
    recipient_list = [user.email]
    message = _("""
    Hello %(name)s:
    </br>
    Your ssh public key has been reset by site administrator.
    Please login and reset your ssh public key.
    </br>
    <a href="%(login_url)s">Login direct</a>

    </br>
    """) % {
        'name': user.name,
        'login_url': reverse('users:login', external=True),
    }
    if settings.DEBUG:
        logger.debug(message)

    send_mail_async.delay(subject, message, recipient_list, html_message=message)


def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        print('valid error')
    return False


def write_login_log(username, name='', login_type='', login_ip='', user_agent=''):
    if not (login_ip and validate_ip(login_ip)):
        login_ip = '0.0.0.0'
    if not name:
        name = username
    login_city = get_ip_city(login_ip)
    LoginLog.objects.create(
        username=username, name=name, login_type=login_type,
        login_ip=login_ip, login_city=login_city, user_agent=user_agent
    )


def get_ip_city(ip, timeout=10):
    # Taobao: http://ip.taobao.com//service/getIpInfo.php?ip=8.8.8.8
    # Sina: http://int.dpool.sina.com.cn/iplookup/iplookup.php?ip=8.8.8.8&format=json

    url = 'http://int.dpool.sina.com.cn/iplookup/iplookup.php?ip=%s&format=json' % ip
    try:
        r = requests.get(url, timeout=timeout)
    except requests.Timeout:
        r = None
    city = 'Unknown'
    if r and r.status_code == 200:
        try:
            data = r.json()
            if not isinstance(data, int) and data['ret'] == 1:
                city = data['country'] + ' ' + data['city']
        except ValueError:
            pass
    return city


def refresh_token(token, user, expiration=None):
    if expiration is None:
        expiration = settings.CONFIG.TOKEN_EXPIRATION or DEFAULT_CACHE_TIME
    cache.set(token, user.id, expiration)


def generate_token(request, user):
    expiration = settings.CONFIG.TOKEN_EXPIRATION or DEFAULT_CACHE_TIME
    remote_addr = request.META.get('REMOTE_ADDR', '')
    if not isinstance(remote_addr, bytes):
        remote_addr = remote_addr.encode("utf-8")
    remote_addr = base64.b16encode(remote_addr)
    token = cache.get('%s_%s' % (user.id, remote_addr))
    if not token:
        token = uuid.uuid4().hex
        cache.set(token, user.id, expiration)
        cache.set('%s_%s' % (user.id, remote_addr), token, expiration)
    return token
