from django.contrib import messages
from django.http import Http404
from loguru import logger
from .models import Notification
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from .serializers import UserNotificationSerializer



class NotificationDeleteView(APIView):
    serializer_class = serializers.Serializer
    def delete(self, request, pk, format=None):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.delete()
            return Response({"message": "Уведомление успешно удалено."}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"message": "Уведомление не найдено."}, status=status.HTTP_404_NOT_FOUND)


class NotificationAllDeleteView(APIView):
    serializer_class = serializers.Serializer

    def delete(self, request, format=None):
        try:
            notifications = Notification.objects.filter(recipient=request.user)
            notifications.delete()
            return Response({"message": "Все уведомления успешно удалены."}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"message": "Ни одно уведомление не найдено."}, status=status.HTTP_404_NOT_FOUND)


class UserNotificationListView(APIView):
    serializer_class = UserNotificationSerializer

    def get(self, request, format=None):
        notifications = Notification.objects.filter(recipient=request.user)
        serializer = self.serializer_class(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)