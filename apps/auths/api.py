# ~*~ coding: utf-8 ~*~

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import get_logger
from .tasks import write_login_log_async
from .utils import generate_token

logger = get_logger(__name__)


class UserToken(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        if not request.user.is_authenticated:
            username = request.data.get('username', '')
            email = request.data.get('email', '')
            password = request.data.get('password', '')
            public_key = request.data.get('public_key', '')

            user, msg = check_user_valid(
                username=username, email=email,
                password=password, public_key=public_key
            )
        else:
            user = request.user
            msg = None
        if user:
            token = generate_token(request, user)
            return Response({'Token': token, 'Keyword': 'Bearer'}, status=200)
        else:
            return Response({'error': msg}, status=406)


class UserAuthApi(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        public_key = request.data.get('public_key', '')
        login_type = request.data.get('login_type', '')
        login_ip = request.data.get('remote_addr', None)
        user_agent = request.data.get('HTTP_USER_AGENT', '')

        if not login_ip:
            login_ip = request.META.get("REMOTE_ADDR")

        user, msg = check_user_valid(
            username=username, password=password,
            public_key=public_key
        )

        if user:
            token = generate_token(request, user)
            write_login_log_async.delay(
                user.username, name=user.name,
                user_agent=user_agent, login_ip=login_ip,
                login_type=login_type
            )
            return Response({'token': token, 'user': user.to_json()})
        else:
            return Response({'msg': msg}, status=401)
