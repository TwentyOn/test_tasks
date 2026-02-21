from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Department, Employee


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def validate_parent_id(self, parent):
        if self.instance and parent:
            if self.instance.pk == parent.pk:
                raise serializers.ValidationError('Отдел не может быть родителем самого себя')
            elif self._would_cycle(self.instance, parent):
                raise serializers.ValidationError('Некорректное значение "parent_id" - циклическая зависимость')
        return parent

    def _would_cycle(self, instance: Department, new_parent: Department) -> bool:
        """
        Метод для проверки циклической зависимости
        :param instance: изменяемый объект
        :param new_parent: родительский объект
        :return: True/False - цикл/нет цикла
        """
        cur_parent = new_parent
        while cur_parent:
            if cur_parent == instance:
                return True
            cur_parent = cur_parent.parent_id


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'department_id': {'read_only': True}
        }


class DetailDepartmentSerializer(serializers.Serializer):
    department = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    def get_department(self, obj) -> DepartmentSerializer:
        dep_serializer = DepartmentSerializer(obj)
        return dep_serializer.data

    @extend_schema_field(EmployeeSerializer)
    def get_employees(self, obj) -> list[dict]:
        include_employees = self.context.get('include_employees', 'true')
        if include_employees.lower() == 'true':
            ee_serializer = EmployeeSerializer(obj.employee_set.all().order_by('created_at'), many=True)
            return ee_serializer.data
        else:
            return []

    @extend_schema_field({
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'department': {'type': 'object'},
                'employees': {'type': 'object'},
                'children': {'type': 'object'},
            }
        }
    })
    def get_children(self, obj) -> list[dict]:
        if self.context['cur_depth'] <= int(self.context['depth']):
            self.context['cur_depth'] += 1

            # многократное обращение к БД, как можно решить?
            children = Department.objects.filter(parent_id=obj.pk)

            return DetailDepartmentSerializer(instance=children, many=True, context=self.context).data
        return []

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context['include_employees'].lower() == 'false':
            del data['employees']
        return data
