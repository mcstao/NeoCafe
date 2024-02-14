from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

from rest_framework import generics, status, permissions, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from services.users.utils import generate_and_send_otp, get_user_from_jwt, generate_jwt
from services.users.otp_validate import OTP
from users.models import CustomUser
from users.serializers import RegistrationSerializer, OtpSerializer, LoginSerializer, AdminLoginSerializer, \
    WaiterLoginSerializer

User = get_user_model()


class CustomerRegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        pre_token = generate_jwt(user)

        otp = generate_and_send_otp(user)

        user.otp = otp
        user.save()

        return Response(
            {"message": f"Введите 4-х значный код, отправленный на почту {user.email}",
             "pre_token": pre_token
             },
            status=status.HTTP_200_OK,
        )


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = OtpSerializer


    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pre_token = request.headers.get("Authorization")
        user = get_user_from_jwt(pre_token)
        if user:
            response = OTP.validate_otp(request)
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


class ConfirmCustomerLoginView(generics.GenericAPIView):
    serializer_class = OtpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pre_token = request.headers.get("Authorization")
        user = get_user_from_jwt(pre_token)
        response = OTP.validate_otp(request)

        if response == status.HTTP_200_OK:

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Код введен неверно, повторите еще раз"}, status=status.HTTP_400_BAD_REQUEST)


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
            if user.check_password(password):
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
            if user.check_password(password):


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


class ConfirmBaristaWaiterLoginView(generics.GenericAPIView):
    serializer_class = OtpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pre_token = request.headers.get("Authorization")
        user = get_user_from_jwt(pre_token)
        response = OTP.validate_otp(request)

        if response == status.HTTP_200_OK:
            if user.is_verified:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                user.is_verified = True
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Код введен неверно, повторите еще раз"}, status=status.HTTP_400_BAD_REQUEST)


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


class ResendOtpView(generics.GenericAPIView):
    serializer_class = serializers.Serializer
    @extend_schema(
        description="Повторная отправка кода",
        responses={200: {"description": "Successful operation"}},
    )

    def get(self, request):

        pre_token = request.headers.get("Authorization")
        user = get_user_from_jwt(pre_token)

        if user:
            generate_and_send_otp(user)
            return Response({"detail": "Код был отправлен заново"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Ошибка при аутентификации пользователя"}, status=status.HTTP_401_UNAUTHORIZED)
