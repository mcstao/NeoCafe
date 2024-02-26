from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from employees.seriaalizers import StaffCreateSerializer
from users.models import CustomUser


class StaffCreateView(generics.CreateAPIView):
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        position = self.request.data.get("position", None)
        if position:
            serializer.validated_data["position"] = position

        serializer.save()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class StaffByBranchView(generics.ListAPIView):
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = CustomUser.objects.filter(position__in=["waiter", "barista"])
        return queryset


class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StaffCreateSerializer
    queryset = CustomUser.objects.filter(position__in=["waiter", "barista"])
    lookup_field = "id"
    permission_classes = [IsAdminUser]



