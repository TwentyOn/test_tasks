from django.shortcuts import render, get_object_or_404
from rest_framework import status, serializers
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.generics import GenericAPIView

from .serializers import DepartmentSerializer, EmployeeSerializer
from .models import Department


# Create your views here.
class DepartmentView(ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    @action(methods=['get'], detail=True)
    def get_department(self, request, pk):
        return Response({'message': 'test'})

    @action(methods=['post'], detail=True, url_path='employee')
    def create_employee(self, request, pk):
        department = get_object_or_404(Department, pk=pk)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(department_id=department)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        print('action', self.action)
        if self.action == 'create_employee':
            return EmployeeSerializer
        else:
            return self.serializer_class
