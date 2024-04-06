from django.http import Http404
from loguru import logger
from .models import Notification
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class NotificationCreateView(APIView):
    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        notification = Notification.objects.create(
            title=title,
            description=description,
            recipient=request.user
        )
        return Response({"id": notification.id}, status=status.HTTP_201_CREATED)

class NotificationDeleteView(APIView):
    def delete(self, request, pk, format=None):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)