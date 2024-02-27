from django.shortcuts import render
from rest_framework import permissions, generics, status
from rest_framework.response import Response

from customers.serializers import CustomerProfileSerializer, CustomerEditProfileSerializer
from services.users.permissions import IsCustomer, IsEmailVerified


class CustomerProfileView(generics.GenericAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsCustomer]

    def get(self, request):
        user = request.user
        serializer = CustomerProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerEditProfileView(generics.GenericAPIView):
    permission_classes = [IsCustomer, IsEmailVerified]
    serializer_class = CustomerEditProfileSerializer

    def put(self, request):
        user = request.user
        first_name = request.data.get("first_name", user.first_name)
        birth_date = request.data.get("birth_date", user.birth_date)
        user.first_name = first_name
        user.birth_date = birth_date
        user.save()
        return Response(
            {"detail": "Профиль успешно изменен"}, status=status.HTTP_200_OK
        )
