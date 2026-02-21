from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

DB_SCHEME_NAME = settings.DB_SCHEME_NAME


# Create your models here.

class Department(models.Model):
    name = models.CharField(blank=False, max_length=200)
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, db_column='parent_id', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = f'{DB_SCHEME_NAME}"."department'
        unique_together = [['name', 'parent_id']]

    def delete_with_mode(self, mode, reassign_to_department_id):
        if mode.lower() == 'cascade':
            self.delete()
        elif mode.lower() == 'reassign':
            if not reassign_to_department_id:
                raise ValidationError('параметр "reassign_to_department_id" обязателен для mode=reassign')

            self.employee_set.update(department_id=reassign_to_department_id)
            # self.department_set.update(parent_id=reassign_to_department_id)

            self.delete()
        else:
            raise ValidationError('Некорректное значение параметра "mode"')


class Employee(models.Model):
    department_id = models.ForeignKey(Department, null=True, on_delete=models.CASCADE, db_column='department_id')
    full_name = models.CharField(blank=False, max_length=200)
    position = models.CharField(blank=False, max_length=200)
    hired_at = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = f'{DB_SCHEME_NAME}"."employee'
