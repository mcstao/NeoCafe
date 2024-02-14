from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from services.users.utils import otp_data

class OTP:
    @staticmethod
    def validate_otp(request):
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        if not email or not otp:
            return status.HTTP_400_BAD_REQUEST

        if email in otp_data:
            if timezone.now() <= otp_data[email]['exp']:
                if otp == otp_data[email]['otp']:
                    return status.HTTP_200_OK
                else:
                    return status.HTTP_400_BAD_REQUEST
            else:
                return status.HTTP_400_BAD_REQUEST
        else:
            return status.HTTP_400_BAD_REQUEST