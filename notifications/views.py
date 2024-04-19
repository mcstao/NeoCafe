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
            messages.success(request, "Уведомление успешно удалено.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            messages.error(request, "Уведомление не найдено.")
            return Response(status=status.HTTP_404_NOT_FOUND)


class NotificationAllDeleteView(APIView):
    serializer_class = serializers.Serializer

    def delete(self, request, format=None):
        try:
            notifications = Notification.objects.filter(recipient=request.user)
            notifications.delete()
            messages.success(request, "Все уведомления успешно удалены.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            messages.error(request, "Ни одно уведомление не найдено.")
            return Response(status=status.HTTP_404_NOT_FOUND)


class UserNotificationListView(APIView):
    serializer_class = UserNotificationSerializer

    def get(self, request, format=None):
        notifications = Notification.objects.filter(recipient=request.user)
        serializer = self.serializer_class(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)