from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.core.exceptions import ValidationError

from .serializers import DepartmentSerializer, EmployeeSerializer, DetailDepartmentSerializer
from .models import Department, Employee


# Create your views here.
class DepartmentView(GenericViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def create(self, request):
        """
        Создание отдела
        :param request:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_path='employee')
    def create_employee(self, request, pk):
        """
        Создание сотрудника
        :param request:
        :param pk:
        :return:
        """
        department = get_object_or_404(Department, pk=pk)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(department_id=department)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request: Request, pk):
        """
        Информация для отдела  (детали + сотрудники + поддерево)
        :param request:
        :param pk:
        :return:
        """
        department = get_object_or_404(Department, pk=pk)

        depth = request.query_params.get('depth', 1)
        include_employees = request.query_params.get('include_employees', 'true')

        serializer = self.get_serializer(
            instance=department,
            context={'include_employees': include_employees, 'depth': depth, 'cur_depth': 1}
        )

        return Response(serializer.data)

    def partial_update(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        serializer = DepartmentSerializer(instance=department, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request: Request, pk):
        department = get_object_or_404(Department, pk=pk)

        mode = request.query_params.get('mode')
        reassign_to_department_id = request.query_params.get('reassign_to_department_id')

        if not mode:
            return Response(
                {'message': 'ошибка входных параметров запроса', 'detail': 'не указан режим удаления "mode"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            department.delete_with_mode(mode, reassign_to_department_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as err:
            return Response(
                {'message': 'ошибка при удалении ресурса', 'detail': str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_serializer_class(self):
        if self.action == 'create_employee':
            return EmployeeSerializer
        elif self.action == 'retrieve':
            return DetailDepartmentSerializer
        else:
            return self.serializer_class
