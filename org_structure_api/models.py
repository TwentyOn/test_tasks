from django.db import models
from django.conf import settings

DB_SCHEME_NAME = settings.DB_SCHEME_NAME


# Create your models here.
class Department(models.Model):
    name = models.CharField(blank=False)
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, db_column='parent_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = f'{DB_SCHEME_NAME}"."department'


class Employee(models.Model):
    department_id = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, db_column='department_id')
    full_name = models.CharField(blank=False)
    position = models.CharField(blank=False)
    hired_at = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = f'{DB_SCHEME_NAME}"."employee'
