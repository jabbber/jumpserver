#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from django.conf.urls import url

from .. import views

app_name = 'auths'

urlpatterns = [
    url(r'^login/$', views.UserLoginView.as_view(), name='login'),
    url(r'^logout/$', views.UserLogoutView.as_view(), name='login'),
]
