from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.db import connection

from org_structure_api.models import Department, Employee


# Create your tests here.
class DepartmentViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department1 = Department.objects.create(name='test_department_1')
        self.department2 = Department.objects.create(name='test_department_2', parent_id=self.department1)

    def test_create_department(self):
        url = reverse('department-list')
        data = {'name': 'new_department', 'parent_id': None}

        # тест создания отдела
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_dep = Department.objects.get(name='new_department')
        self.assertEqual(new_dep.parent_id, None)

    def test_create_employee(self):
        url = reverse('department-create-employee', kwargs={'pk': self.department1.pk})
        data = {"full_name": "Alex", "position": "programmer", "hired_at": "2026-02-22"}

        # тест создания сотрудника
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data['full_name'], 'Alex')
        new_employee = Employee.objects.get(full_name='Alex')
        self.assertEqual(new_employee.position, 'programmer')

    def test_get_detail_department(self):
        url1 = reverse('department-detail', kwargs={'pk': self.department1.pk})
        url2 = reverse('department-detail', kwargs={'pk': self.department2.pk})

        # тест объекта без родителей
        response1 = self.client.get(url1)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data['department']), 4)
        self.assertEqual(response1.data['department']['name'], 'test_department_1')
        self.assertEqual(response1.data['department']['parent_id'], None)

        # тест объекта дочернего объекта
        response2 = self.client.get(url2)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data['department']), 4)
        self.assertEqual(response2.data['department']['name'], 'test_department_2')
        self.assertEqual(response2.data['department']['parent_id'], self.department1.pk)

    def test_patch_department(self):
        # тест частичного изменения
        url = reverse('department-detail', kwargs={'pk': self.department2.pk})
        data = {'name': 'update_department', 'parent_id': None}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.department2.refresh_from_db()
        self.assertEqual(self.department2.name, 'update_department')
        self.assertEqual(self.department2.parent_id, None)

    def test_delete_department(self):
        # тест каскадного удаления
        url = reverse('department-detail', kwargs={'pk': self.department1.pk}, query={'mode': 'cascade'})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Department.objects.count(), 0)
