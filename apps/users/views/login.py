# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals
from django import forms
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.shortcuts import reverse, redirect
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView
from formtools.wizard.views import SessionWizardView
from django.conf import settings

from common.utils import get_object_or_none
from ..models import User
from ..utils import send_reset_password_mail
from .. import forms


__all__ = [
    'UserForgotPasswordView', 'UserForgotPasswordSendMailSuccessView',
    'UserResetPasswordView', 'UserResetPasswordSuccessView',
    'UserFirstLoginView'
]


class UserForgotPasswordView(TemplateView):
    template_name = 'users/forgot_password.html'

    def post(self, request):
        email = request.POST.get('email')
        user = get_object_or_none(User, email=email)
        if not user:
            msg = _('Email address invalid, please input again')
            return self.get(request, errors=msg)
        else:
            send_reset_password_mail(user)
            return HttpResponseRedirect(
                reverse('users:forgot-password-sendmail-success')
            )


class UserForgotPasswordSendMailSuccessView(TemplateView):
    template_name = 'flash_message_standalone.html'

    def get_context_data(self, **kwargs):
        context = {
            'title': _('Send reset password message'),
            'messages': _('Send reset password mail success, '
                          'login your mail box and follow it '),
            'redirect_url': reverse('users:login'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class UserResetPasswordSuccessView(TemplateView):
    template_name = 'flash_message_standalone.html'

    def get_context_data(self, **kwargs):
        context = {
            'title': _('Reset password success'),
            'messages': _('Reset password success, return to login page'),
            'redirect_url': reverse('users:login'),
            'auto_redirect': True,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class UserResetPasswordView(TemplateView):
    template_name = 'users/reset_password.html'

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        user = User.validate_reset_token(token)

        if not user:
            kwargs.update({'errors': _('Token invalid or expired')})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        password = request.POST.get('password')
        password_confirm = request.POST.get('password-confirm')
        token = request.GET.get('token')

        if password != password_confirm:
            return self.get(request, errors=_('Password not same'))

        user = User.validate_reset_token(token)
        if not user:
            return self.get(request, errors=_('Token invalid or expired'))

        user.reset_password(password)
        return HttpResponseRedirect(reverse('users:reset-password-success'))


class UserFirstLoginView(LoginRequiredMixin, SessionWizardView):
    template_name = 'users/first_login.html'
    form_list = [forms.UserProfileForm, forms.UserPublicKeyForm]
    file_storage = default_storage

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and not request.user.is_first_login:
            return redirect(reverse('index'))
        return super().dispatch(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        user = self.request.user
        for form in form_list:
            for field in form:
                if field.value():
                    setattr(user, field.name, field.value())
                if field.name == 'enable_otp':
                    user.enable_otp = field.value()
        user.is_first_login = False
        user.is_public_key_valid = True
        user.save()
        context = {
            'user_guide_url': settings.CONFIG.USER_GUIDE_URL
        }
        return render(self.request, 'users/first_login_done.html', context)

    def get_context_data(self, **kwargs):
        context = super(UserFirstLoginView, self).get_context_data(**kwargs)
        context.update({'app': _('Users'), 'action': _('First login')})
        return context

    def get_form_initial(self, step):
        user = self.request.user
        if step == '0':
            return {
                'username': user.username or '',
                'name': user.name or user.username,
                'email': user.email or '',
                'wechat': user.wechat or '',
                'phone': user.phone or ''
            }
        return super().get_form_initial(step)

    def get_form(self, step=None, data=None, files=None):
        form = super(UserFirstLoginView, self).get_form(step, data, files)
        form.instance = self.request.user
        return form
