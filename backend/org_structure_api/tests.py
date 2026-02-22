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
        self.department3 = Department.objects.create(name='test_department_3', parent_id=self.department2)

    def test_create_department(self):
        """
        Тест создания объекта department
        """

        url = reverse('department-list')
        data = {'name': 'new_department', 'parent_id': None}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_dep = Department.objects.get(name='new_department')
        self.assertEqual(new_dep.parent_id, None)

    def test_create_employee(self):
        """
        Тест создания объекта employee
        """

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
        """
        Тест запроса деталей об объекте department
        """

        url1 = reverse('department-detail', kwargs={'pk': self.department1.pk})
        url2 = reverse('department-detail', kwargs={'pk': self.department2.pk})
        url3 = reverse(
            'department-detail',
            kwargs={'pk': self.department1.pk},
            query={'include_employees': 'false'}
        )

        self.department1.employee_set.create(
            full_name="Alex",
            position="programmer",
            hired_at="2026-02-22"
        )

        # тест объекта без родителей
        response1 = self.client.get(url1)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data), 3)
        self.assertEqual(len(response1.data['department']), 4)
        self.assertEqual(response1.data['department']['name'], 'test_department_1')
        self.assertEqual(response1.data['department']['parent_id'], None)

        # тест дочернего объекта
        response2 = self.client.get(url2)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data['department']), 4)
        self.assertEqual(response2.data['department']['name'], 'test_department_2')
        self.assertEqual(response2.data['department']['parent_id'], self.department1.pk)

        # тест параметр запроса include_employees=false
        response3 = self.client.get(url3)
        self.assertEqual(len(response3.data), 2)

    def test_patch_department(self):
        """
        Тест частичного обновления объекта department
        """

        url = reverse('department-detail', kwargs={'pk': self.department2.pk})
        original_name = self.department2.name
        original_parent = self.department2.parent_id

        # тест создания циклической зависимости
        data1 = {'name': 'update_department', 'parent_id': self.department3.pk}
        response1 = self.client.patch(url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.department2.refresh_from_db()
        self.assertEqual(self.department2.name, original_name)
        self.assertEqual(self.department2.parent_id, original_parent)

        # тест назначения родителем самого себя
        data2 = {'parent_id': self.department2.pk}
        response2 = self.client.patch(url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.department2.refresh_from_db()
        self.assertEqual(self.department2.parent_id, original_parent)

        # тест обновления
        data3 = {'name': 'update_department', 'parent_id': None}
        response3 = self.client.patch(url, data3, format='json')
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.department2.refresh_from_db()
        self.assertEqual(self.department2.name, 'update_department')
        self.assertEqual(self.department2.parent_id, None)

    def test_cascade_delete_department(self):
        """
        Тест удаления объекта department в режиме cascade
        """

        url = reverse('department-detail', kwargs={'pk': self.department1.pk}, query={'mode': 'cascade'})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Department.objects.count(), 0)

    def test_reassign_delete_department(self):
        """
        Тест удаления объекта department в режиме reassign
        """
        url1 = reverse(
            'department-detail',
            kwargs={'pk': self.department3.pk},
            query={'mode': 'reassign'}
        )
        url2 = reverse(
            'department-detail',
            kwargs={'pk': self.department3.pk},
            query={'mode': 'reassign', 'reassign_to_department_id': self.department1.pk}
        )

        # тест без параметра reassign_to_department_id
        response = self.client.delete(url1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Department.objects.filter(pk=self.department3.pk).exists())

        # тест с параметром
        employee = self.department3.employee_set.create(
            full_name="Alex",
            position="programmer",
            hired_at="2026-02-22"
        )
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Department.objects.count(), 2)
        self.assertIn(employee, self.department1.employee_set.all())
