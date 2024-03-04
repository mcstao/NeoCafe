from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from services.users.permissions import IsWaiter, IsEmailVerified
from waiters.serializers import WaiterProfileSerializer


class WaiterProfileView(generics.GenericAPIView):
    serializer_class = WaiterProfileSerializer
    permission_classes = [IsWaiter, IsEmailVerified]

    def get(self, request):
        user = request.user
        serializer = WaiterProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
