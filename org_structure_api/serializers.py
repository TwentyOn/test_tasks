from rest_framework import serializers

from .models import Department, Employee


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True}
        }


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True}
        }


class DetailDepartmentSerializer(serializers.Serializer):
    department = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    def get_department(self, obj):
        dep_serializer = DepartmentSerializer(obj)
        return dep_serializer.data

    def get_employees(self, obj):
        include_employees = self.context.get('include_employees', 'true')
        if include_employees.lower() == 'true':
            ee_serializer = EmployeeSerializer(obj.employee_set.all().order_by('created_at'), many=True)
            return ee_serializer.data
        else:
            return None

    def get_children(self, obj):
        if self.context['cur_depth'] <= int(self.context['depth']):
            self.context['cur_depth'] += 1

            # многократное обращение к БД, как можно решить?
            children = Department.objects.filter(parent_id=obj.pk)

            return DetailDepartmentSerializer(instance=children, many=True, context=self.context).data
        return []

    # def get_children(self, obj):
    #     depth = int(self.context.get('depth', 1))
    #     cur_depth = self.context.get('cur_depth')
    #     print(cur_depth)
    #
    #     if cur_depth >= depth:
    #         return []
    #     new_context = self.context.copy()
    #     new_context['cur_depth'] += 1
    #     children = Department.objects.filter(parent_id=obj.id)
    #     return DepartmentSerializer(children, many=True, context=new_context).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context['include_employees'].lower() == 'false':
            del data['employees']
        return data
