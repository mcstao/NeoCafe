import jwt
from django.conf import settings

import secrets

from django.core.mail import send_mail
from django.utils import timezone

from Neocafe24 import settings
from users.models import CustomUser




def generate_and_send_otp(user):

    otp = "".join([str(secrets.randbelow(10)) for _ in range(4)])

    user.expiration_time = timezone.now() + timezone.timedelta(minutes=5)
    user.otp = otp
    subject = 'Подтверждение адреса электронной почты'
    message = f'Ваш одноразовый код подтверждения: {user.otp}'
    send_mail(subject, message, settings.EMAIL_FROM, [user.email])
    user.save()


def generate_jwt(user):
    payload = {'id': user.id, 'email': str(user.email), 'exp': timezone.now() + timezone.timedelta(hours=1), "pre_2fa_auth": True}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def get_user_from_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = CustomUser.objects.get(id=payload["id"])
        return user
    except CustomUser.DoesNotExist:
        return None
    except jwt.DecodeError:
        return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
