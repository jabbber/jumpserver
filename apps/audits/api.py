# ~*~ coding: utf-8 ~*~
# 

from __future__ import absolute_import, unicode_literals

from rest_framework import generics, viewsets
from rest_framework_bulk import BulkModelViewSet

# from audits.backends import command_store, record_store
# from audits.backends.command.serializers import CommandLogSerializer
# from audits.backends.record.serializers import RecordSerializer
# from common.permissions import IsSuperUserOrAppUser, IsAppUser
# from . import models, serializers


class ProxyLogReceiveView(generics.CreateAPIView):
    pass
    # queryset = models.ProxyLog.objects.all()
    # serializer_class = serializers.ProxyLogSerializer
    # permission_classes = (IsAppUser,)
    #
    # def get_serializer(self, *args, **kwargs):
    #     kwargs['data']['terminal'] = self.request.user.terminal.name
    #     return super(ProxyLogReceiveView, self).get_serializer(*args, **kwargs)


class ProxyLogViewSet(viewsets.ModelViewSet):
    """User proxy to backend server need call this api.

    params: {
        "username": "",
        "name": "",
        "hostname": "",
        "ip": "",
        "terminal": "",
        "login_type": "",
        "system_user": "",
        "was_failed": "",
        "date_start": ""
    }

    """
    pass

    # queryset = models.ProxyLog.objects.all()
    # serializer_class = serializers.ProxyLogSerializer
    # permission_classes = (IsSuperUserOrAppUser,)


class CommandLogViewSet(BulkModelViewSet):
    """接受app发送来的command log, 格式如下
    {
        "proxy_log_id": 23,
        "user": "admin",
        "asset": "localhost",
        "system_user": "web",
        "command_no": 1,
        "command": "whoami",
        "output": "d2hvbWFp",  # base64.b64encode(s)
        "timestamp": 1485238673.0
    }

    """
    # queryset = command_store.all()
    # serializer_class = CommandLogSerializer
    # permission_classes = (IsSuperUserOrAppUser,)
    pass


class RecordLogViewSet(BulkModelViewSet):
    """接受app发送来的record log, 格式如下
        {
            "proxy_log_id": 23,
            "output": "d2hvbWFp",  # base64.b64encode(s)
            "timestamp": 1485238673.0
        }
    """
    pass

    # serializer_class = RecordSerializer
    # permission_classes = (IsSuperUserOrAppUser,)
    #
    # def get_queryset(self):
    #     filter_kwargs = {}
    #     proxy_log_id = self.request.query_params.get('proxy_log_id')
    #     data_from_ts = self.request.query_params.get('date_from_ts')
    #     if proxy_log_id:
    #         filter_kwargs['proxy_log_id'] = proxy_log_id
    #     if data_from_ts:
    #         filter_kwargs['date_from_ts'] = data_from_ts
    #     if filter_kwargs:
    #         return record_store.filter(**filter_kwargs)
    #     else:
    #         return record_store.all()
