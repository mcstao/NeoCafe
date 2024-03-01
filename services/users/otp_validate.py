
import logging


from django.utils import timezone
from rest_framework import status




logger = logging.getLogger(__name__)
class OTP:
    @staticmethod
    def validate_otp(request, user):
        try:
            email = request.POST.get('email')
            otp = request.POST.get('otp')

            if not email or not otp:
                logger.error("Invalid email or OTP provided")
                return status.HTTP_400_BAD_REQUEST
            if timezone.now() <= user.expiration_time:
                if otp == user.otp:
                    logger.info("OTP successfully validated")
                    return status.HTTP_200_OK
                else:
                    logger.error("Invalid OTP provided")
                    return status.HTTP_400_BAD_REQUEST
            else:
                logger.error("OTP expired")
                return status.HTTP_400_BAD_REQUEST
        except Exception as e:
            logger.exception("An error occurred during OTP validation: %s", str(e))
            return status.HTTP_500_INTERNAL_SERVER_ERROR
