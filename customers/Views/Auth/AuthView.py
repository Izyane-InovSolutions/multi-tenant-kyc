import logging

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema

from customers.Serializers.Login.LoginSerializers import LoginSerializer, RefreshSerializer



logger = logging.getLogger(__name__)


def _is_mobile(request):
    return request.headers.get('X-Client-Type', 'web').lower() == 'mobile'


def _cookie_kwargs():
    return {
        "httponly": True,
        "secure": settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', True),
        "samesite": settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax'),
        "path": '/',
    }


def _set_auth_cookies(response, access, refresh):
    kwargs = _cookie_kwargs()
    response.set_cookie(
        settings.SIMPLE_JWT['AUTH_COOKIE'], access,
        max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
        **kwargs,
    )
    response.set_cookie(
        settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'], refresh,
        max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
        **kwargs,
    )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer

    @extend_schema(summary="Admin login", request=LoginSerializer, tags=["Auth"])
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = authenticate(
                request,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
            )
            if user is None:
                return Response(
                    {"status": "fail", "message": "Invalid email or password", "data": None},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not user.is_active:
                return Response(
                    {"status": "fail", "message": "Account is inactive", "data": None},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if not user.is_staff:
                return Response(
                    {"status": "fail", "message": "You do not have administrator access", "data": None},
                    status=status.HTTP_403_FORBIDDEN,
                )

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            user_data = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_superuser": user.is_superuser,
            }

            if _is_mobile(request):
                return Response(
                    {
                        "status": "success",
                        "message": "Login successful",
                        "data": {"user": user_data, "access": str(access), "refresh": str(refresh)},
                    },
                    status=status.HTTP_200_OK,
                )

            response = Response(
                {"status": "success", "message": "Login successful", "data": {"user": user_data}},
                status=status.HTTP_200_OK,
            )
            _set_auth_cookies(response, str(access), str(refresh))
            return response

        except Exception as e:
            logger.exception("Login failed")
            return Response(
                {"status": "fail", "message": "Something went wrong", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = RefreshSerializer

    @extend_schema(summary="Refresh access token", request=RefreshSerializer, tags=["Auth"])
    def post(self, request):
        try:
            if _is_mobile(request):
                raw_refresh = request.data.get('refresh')
            else:
                raw_refresh = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

            if not raw_refresh:
                return Response(
                    {"status": "fail", "message": "Refresh token missing", "data": None},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            refresh = RefreshToken(raw_refresh)
            access = refresh.access_token

            if _is_mobile(request):
                return Response(
                    {"status": "success", "message": "Token refreshed", "data": {"access": str(access)}},
                    status=status.HTTP_200_OK,
                )

            response = Response(
                {"status": "success", "message": "Token refreshed", "data": None},
                status=status.HTTP_200_OK,
            )
            kwargs = _cookie_kwargs()
            response.set_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE'], str(access),
                max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                **kwargs,
            )
            return response

        except TokenError as e:
            return Response(
                {"status": "fail", "message": "Invalid or expired refresh token", "data": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            logger.exception("Refresh failed")
            return Response(
                {"status": "fail", "message": "Something went wrong", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Logout", tags=["Auth"])
    def post(self, request):
        try:
            if _is_mobile(request):
                raw_refresh = request.data.get('refresh')
            else:
                raw_refresh = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

            if raw_refresh:
                try:
                    RefreshToken(raw_refresh).blacklist()
                except TokenError:
                    pass

            response = Response(
                {"status": "success", "message": "Logged out successfully", "data": None},
                status=status.HTTP_200_OK,
            )
            if not _is_mobile(request):
                response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'], path='/')
                response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'], path='/')
            return response

        except Exception as e:
            logger.exception("Logout failed")
            return Response(
                {"status": "fail", "message": "Something went wrong", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )