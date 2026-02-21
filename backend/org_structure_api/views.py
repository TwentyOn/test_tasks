from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .serializers import DepartmentSerializer, EmployeeSerializer, DetailDepartmentSerializer
from .models import Department
from .openapi_error_schemes import BAD_REQUEST_RESP_SCHEMA, NOT_FOUND_RESP_SCHEMA


# Create your views here.
class DepartmentView(GenericViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    @extend_schema(
        responses={
            201: DepartmentSerializer,
            400: BAD_REQUEST_RESP_SCHEMA
        }
    )
    def create(self, request):
        """
        Создание отдела
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        responses={
            201: DepartmentSerializer,
            400: BAD_REQUEST_RESP_SCHEMA,
            404: NOT_FOUND_RESP_SCHEMA
        })
    @action(methods=['post'], detail=True, url_path='employee')
    def create_employee(self, request, pk):
        """
        Создание сотрудника в отделе
        """
        department = get_object_or_404(Department, pk=pk)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(department_id=department)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='depth', location=OpenApiParameter.QUERY, type=int, default=1,
                description='глубина вложенных подразделений в ответе'),
            OpenApiParameter(
                name='include_employees', location=OpenApiParameter.QUERY, type=bool, default=True,
                description='включать сотрудников в ответ')
        ],
        responses={
            200: DetailDepartmentSerializer,
            400: BAD_REQUEST_RESP_SCHEMA,
            404: NOT_FOUND_RESP_SCHEMA
        }
    )
    def retrieve(self, request: Request, pk):
        """
        Информация для отдела  (детали + сотрудники + поддерево)
        """
        department = get_object_or_404(Department, pk=pk)

        depth = request.query_params.get('depth', 1)
        include_employees = request.query_params.get('include_employees', 'true')

        serializer = self.get_serializer(
            instance=department,
            context={'include_employees': include_employees, 'depth': depth, 'cur_depth': 1}
        )

        return Response(serializer.data)

    @extend_schema(
        responses={
            200: DepartmentSerializer,
            400: BAD_REQUEST_RESP_SCHEMA,
            404: NOT_FOUND_RESP_SCHEMA
        }
    )
    def partial_update(self, request, pk):
        """
        Частичное обновление объекта "отдел"
        """
        department = get_object_or_404(Department, pk=pk)
        serializer = self.get_serializer(instance=department, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='mode', location=OpenApiParameter.QUERY, type=str,
                description='''
                Режим удаления
                cascade — удалить подразделение, всех сотрудников и все дочерние подразделения 
                reassign — удалить подразделение, а сотрудников перевести в reassign_to_department_id''',
                enum=['cascade', 'reassign']
            ),
            OpenApiParameter(
                name='reassign_to_department_id', location=OpenApiParameter.QUERY, type=int,
                description='''
                обязателен, если mode=reassign
                '''
            )
        ],
        responses={
            204: None,
            400: BAD_REQUEST_RESP_SCHEMA,
            404: NOT_FOUND_RESP_SCHEMA
        }
    )
    def destroy(self, request: Request, pk):
        """
        Удаление отдела
        """
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
