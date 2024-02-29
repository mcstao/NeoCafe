from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from django.contrib.auth.hashers import check_password
from rest_framework import generics, status, permissions, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from services.users.utils import generate_and_send_otp, get_user_from_jwt, generate_jwt
from services.users.otp_validate import OTP, logger
from users.models import CustomUser
from users.serializers import RegistrationSerializer, OtpSerializer, LoginSerializer, AdminLoginSerializer, \
    WaiterLoginSerializer

User = get_user_model()


@extend_schema(
    description='Этот эндпоинт предназначен для регистрации клиентов.',
    request={
        'content': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string', 'format': 'email'}
                    },
                    'required': ['email']
        }
    },
    responses={
        200: {
                    'example': {
                        'message': 'Введите 4-значный код, отправленный на почту example@gmail.com',
                        'pre_token': 'your_pre_token_here'
                    }
            }
    }
)
class CustomerRegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        pre_token = generate_jwt(user)

        generate_and_send_otp(user)



        return Response(
            {"message": f"Введите 4-х значный код, отправленный на почту {user.email}",
             "pre_token": pre_token
             },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    description='Этот эндпоинт служит для подтверждении регистрации пользователей',
    request={
        'headers': {
                    'type': 'object',
                    'properties': {
                        'Authorization': 'pre_token'
                    },
                    'required': ['Authorization'],
                    'example':{
                        'Authorization': 'pre_token'
                    }
         },
        'content': {
                    'type': 'object',
                    'properties': {
                        'otp': {'type': 'string'},
                        'email': {'type': 'string', 'format': 'email'},
                    },
                    'required': ['otp', 'email'],
        }
    },
    responses={
        200: {
            'example': {
                'message': 'Поздравляем, ваш адрес электронной почты подтвержден!'
            }
        }

    }
)
class VerifyEmailView(generics.GenericAPIView):
    serializer_class = OtpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pre_token = request.headers.get("Authorization")
        user = get_user_from_jwt(pre_token)
        if user:

            response = OTP.validate_otp(request, user)
            if response == status.HTTP_200_OK:
                user.is_verified = True
                user.save()
                return Response(
                    {"detail": "Поздравляем, ваш адрес электронной почты подтвержден!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"detail": "Код введен неверно, повторите еще раз"},
                    status=response,
                )
        else:
            return Response({"detail": "Ошибка при аутентификации пользователя"}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    description='Этот эндпоинт предназначен для входа клиентов.',
    request={
        'content': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string', 'format': 'email'}
                    },
                    'required': ['email']
        }
    },
    responses={
        200: {
                    'example': {
                        'message': 'Введите 4-значный код, отправленный на почту example@gmail.com',
                        'pre_token': 'your_pre_token_here'
                    }
            }
    }
)
class CustomerLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get("email")

        try:
            user = CustomUser.objects.get(email=email)
            generate_and_send_otp(user)
            pre_token = generate_jwt(user)
            return Response(
                {"message": f"Введите 4-х значный код, отправленный на почту {user.email}",
                 "pre_token": pre_token},
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Пользователь с указанным адресом электронной почты не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )


@extend_schema(
    description='Этот эндпоинт служит для подтверждении входа клиентов по коду',
    request={
        'headers': {
                    'type': 'object',
                    'properties': {
                        'Authorization': 'pre_token'
                    },
                    'required': ['Authorization'],
                    'example':{
                        'Authorization': 'pre_token'
                    }
         },
        'content': {
                    'type': 'object',
                    'properties': {
                        'otp': {'type': 'string'},
                        'email': {'type': 'string', 'format': 'email'},
                    },
                    'required': ['otp', 'email'],
        }
    },
    responses={
        200: {
            'example': {
                'refresh': 'token',
                'access': 'token'
            }
        }

    }
)
class ConfirmCustomerLoginView(generics.GenericAPIView):
    serializer_class = OtpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pre_token = request.headers.get("Authorization")
        user = get_user_from_jwt(pre_token)
        response = OTP.validate_otp(request, user)

        if response == status.HTTP_200_OK:

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Код введен неверно, повторите еще раз"}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    description='Этот эндпоинт служит для входа админа',
    responses={
        200: {
            'example': {
                'refresh': 'token',
                'access': 'token'
            }
        }

    }
)
class AdminLoginView(generics.GenericAPIView):
    serializer_class = AdminLoginSerializer

    def post(self, request):
        username = request.data["username"]
        password = request.data["password"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND
            )
        if user.position == "admin":
            if user.password == password:
                refresh = RefreshToken.for_user(user)

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Неверный пароль"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "Пользователь не является администратором"},
                status=status.HTTP_400_BAD_REQUEST,
            )



@extend_schema(
    description='Этот эндпоинт предназначен для входа официантов.',
    responses={
        200: {
                    'example': {
                        'message': 'Введите 4-значный код, отправленный на почту example@gmail.com',
                        'pre_token': 'your_pre_token_here'
                    }
            }
    }
)
class WaiterLoginView(generics.GenericAPIView):
    serializer_class = WaiterLoginSerializer

    def post(self, request):
        username = request.data["username"]
        password = request.data["password"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        if user.position == "waiter":
            if user.password == password:

                try:

                    pre_token = generate_jwt(user)
                    generate_and_send_otp(user)
                    return Response(
                        {"message": f"Введите 4-х значный код, отправленный на почту {user.email}",
                         "pre_token": pre_token},
                        status=status.HTTP_200_OK,
                    )
                except CustomUser.DoesNotExist:
                    return Response(
                        {"error": "Пользователь с указанным адресом электронной почты не найден."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                return Response(
                    {"detail": "Неправильный пароль"}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"detail": "Пользователь не является официантом"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(
    description='Этот эндпоинт служит для подтверждении входа сотрудников по коду',
    request={
        'headers': {
                    'type': 'object',
                    'properties': {
                        'Authorization': 'pre_token'
                    },
                    'required': ['Authorization'],
                    'example':{
                        'Authorization': 'pre_token'
                    }
         },
        'content': {
                    'type': 'object',
                    'properties': {
                        'otp': {'type': 'string'},
                        'email': {'type': 'string', 'format': 'email'},
                    },
                    'required': ['otp', 'email'],
        }
    },
    responses={
        200: {
            'example': {
                'refresh': 'token',
                'access': 'token'
            }
        }

    }
)
class ConfirmBaristaWaiterLoginView(generics.GenericAPIView):
    serializer_class = OtpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pre_token = request.headers.get("Authorization")
        user = get_user_from_jwt(pre_token)
        response = OTP.validate_otp(request, user)

        if response == status.HTTP_200_OK:
            if not user.is_verified:
                user.is_verified = True
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Код введен неверно, повторите еще раз"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Этот эндпоинт предназначен для входа бармена.',
    request={
        'content': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string', 'format': 'email'}
                    },
                    'required': ['email']
        }
    },
    responses={
        200: {
                    'example': {
                        'message': 'Введите 4-значный код, отправленный на почту example@gmail.com',
                        'pre_token': 'your_pre_token_here'
                    }
            }
    }
)
class BaristaLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND
            )
        if user.position == "barista":
            try:
                user = CustomUser.objects.get(email=email)
                pre_token = generate_jwt(user)
                generate_and_send_otp(user)
                return Response(
                    {"message": f"Введите 4-х значный код, отправленный на почту {user.email}",
                     "pre_token": pre_token},
                    status=status.HTTP_200_OK,
                )
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "Пользователь с указанным адресом электронной почты не найден."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"detail": "Пользователь не является барменом"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(
    description='Повторная отправка кода'
                ' Ожидается, что клиент передаст pre_token пользователя в заголовке Authorization.',
    responses={
        200: {
            'example': {
                        "detail": "Код был отправлен заново"
            }
        }

    }
)
class ResendOtpView(generics.GenericAPIView):
    serializer_class = serializers.Serializer


    def get(self, request):

        pre_token = request.headers.get("Authorization")
        user = get_user_from_jwt(pre_token)

        if user:
            generate_and_send_otp(user)
            return Response({"detail": "Код был отправлен заново"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Ошибка при аутентификации пользователя"}, status=status.HTTP_401_UNAUTHORIZED)
