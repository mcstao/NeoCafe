from rest_framework import viewsets, permissions
from .models import Branch
from .serializers import ScheduleSerializer, BranchSerializer


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    # permission_classes = [permissions.IsAdminUser]
