from django.shortcuts import render, get_object_or_404
from rest_framework import status, serializers
from rest_framework.viewsets import ViewSet, ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

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

        serializer = DetailDepartmentSerializer(
            department,
            context={'include_employees': include_employees, 'depth': depth, 'cur_depth': 1}
        )
        data = serializer.data
        # children = self.get_dep_children(data, include_employees, depth)
        # data['children'] = children

        return Response(data)

    def get_dep_children(self, initial_data, include_employees, depth, cur_depth=1):
        print(depth, cur_depth)
        result = []
        parent_id = initial_data['department']['id']
        children = Department.objects.filter(parent_id=parent_id)
        if children.exists():
            initial_data['children'] = []
            for child in children:
                serializer = DetailDepartmentSerializer(child, context={'include_employees': include_employees})
                data = serializer.data
                initial_data['children'].append(data)
                result.append(data)

        if cur_depth < int(depth):
            for item in result:
                self.get_dep_children(item, include_employees, depth, cur_depth + 1)
        return result


    def get_serializer_class(self):
        print('action', self.action)
        if self.action == 'create_employee':
            return EmployeeSerializer
        else:
            return self.serializer_class
