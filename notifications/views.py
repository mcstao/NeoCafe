from django.http import Http404
from loguru import logger
from .models import Notification
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers



class NotificationDeleteView(APIView):
    serializer_class = serializers.Serializer
    def delete(self, request, pk, format=None):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)