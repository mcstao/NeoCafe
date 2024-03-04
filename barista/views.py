from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from barista.serializers import BaristaProfileSerializer
from services.users.permissions import IsBarista, IsEmailVerified


class BaristaProfileView(generics.GenericAPIView):
    serializer_class = BaristaProfileSerializer
    permission_classes = [IsBarista, IsEmailVerified]

    def get(self, request):
        user = request.user
        serializer = BaristaProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
