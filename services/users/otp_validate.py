import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from services.users.utils import otp_data

logger = logging.getLogger(__name__)
class OTP:
    @staticmethod
    def validate_otp(request, user):
        user.email = request.POST.get('email')
        user.otp = request.POST.get('otp')


        logger.info(f"Received email: {user.email}, OTP: {user.otp}")

        if not user.email or not user.otp:
            logger.error("Invalid email or OTP provided")
            return status.HTTP_400_BAD_REQUEST

        if user.email in otp_data:
            if timezone.now() <= otp_data[user.email]['exp']:
                if user.otp == otp_data[user.email]['user.otp']:
                    logger.info("OTP successfully validated")
                    return status.HTTP_200_OK
                else:
                    logger.error("Invalid OTP provided")
                    return status.HTTP_400_BAD_REQUEST
            else:
                logger.error("OTP expired")
                return status.HTTP_400_BAD_REQUEST
        else:
            logger.error("No OTP data found for the email")
            return status.HTTP_400_BAD_REQUEST
