from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Task, Project, Area, Tag
from categories.models import Category

class TaskCRUDTestCase(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Создаем тестовую категорию
        self.category = Category.objects.create(
            name='Test Category'
        )
        
        # Создаем тестовый проект
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Project Description',
            owner=self.user
        )
        
        # Создаем тестовую область
        self.area = Area.objects.create(
            name='Test Area',
            description='Test Area Description',
            owner=self.user
        )
        
        # Создаем тестовый тег
        self.tag = Tag.objects.create(
            name='Test Tag',
            owner=self.user
        )
        
        # Создаем тестовую задачу
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Task Description',
            owner=self.user,
            category=self.category,
            project=self.project,
            area=self.area,
            created_date=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=7)
        )
        self.task.tags.add(self.tag)
        
        # Создаем клиент для тестирования
        self.client = Client()
        
        # Авторизуем пользователя
        self.client.login(username='testuser', password='testpassword')
    
    def test_task_list_view(self):
        """Тест для проверки списка задач"""
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_list.html')
        self.assertContains(response, 'Test Task')
    
    def test_task_detail_view(self):
        """Тест для проверки детального просмотра задачи"""
        response = self.client.get(reverse('task_detail', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_detail.html')
        self.assertContains(response, 'Test Task')
        self.assertContains(response, 'Test Task Description')
    
    def test_task_create_view(self):
        """Тест для проверки создания задачи"""
        task_count = Task.objects.count()
        response = self.client.post(reverse('task_create'), {
            'title': 'New Test Task',
            'description': 'New Test Task Description',
            'category': self.category.id,
            'project': self.project.id,
            'area': self.area.id,
            'tags': [self.tag.id],
            'deadline': timezone.now() + timezone.timedelta(days=14)
        })
        # Проверяем, что произошел редирект после успешного создания
        self.assertEqual(response.status_code, 302)
        # Проверяем, что задача была создана
        self.assertEqual(Task.objects.count(), task_count + 1)
        # Проверяем, что задача создана с правильными данными
        new_task = Task.objects.latest('id')
        self.assertEqual(new_task.title, 'New Test Task')
        self.assertEqual(new_task.description, 'New Test Task Description')
        self.assertEqual(new_task.owner, self.user)
    
    def test_task_update_view(self):
        """Тест для проверки обновления задачи"""
        response = self.client.post(reverse('task_update', args=[self.task.id]), {
            'title': 'Updated Test Task',
            'description': 'Updated Test Task Description',
            'category': self.category.id,
            'project': self.project.id,
            'area': self.area.id,
            'tags': [self.tag.id],
            'deadline': timezone.now() + timezone.timedelta(days=21)
        })
        # Проверяем, что произошел редирект после успешного обновления
        self.assertEqual(response.status_code, 302)
        # Проверяем, что задача была обновлена с правильными данными
        updated_task = Task.objects.get(id=self.task.id)
        self.assertEqual(updated_task.title, 'Updated Test Task')
        self.assertEqual(updated_task.description, 'Updated Test Task Description')
    
    def test_task_delete_view(self):
        """Тест для проверки удаления задачи"""
        task_count = Task.objects.count()
        response = self.client.post(reverse('task_delete', args=[self.task.id]))
        # Проверяем, что произошел редирект после успешного удаления
        self.assertEqual(response.status_code, 302)
        # Проверяем, что задача была удалена
        self.assertEqual(Task.objects.count(), task_count - 1)
        # Проверяем, что задачи больше нет в базе данных
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=self.task.id)

class ProjectCRUDTestCase(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Создаем тестовый проект
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Project Description',
            owner=self.user
        )
        
        # Создаем клиент для тестирования
        self.client = Client()
        
        # Авторизуем пользователя
        self.client.login(username='testuser', password='testpassword')
    
    def test_project_list_view(self):
        """Тест для проверки списка проектов"""
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/project_list.html')
        self.assertContains(response, 'Test Project')
    
    def test_project_detail_view(self):
        """Тест для проверки детального просмотра проекта"""
        response = self.client.get(reverse('project_detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/project_detail.html')
        self.assertContains(response, 'Test Project')
        self.assertContains(response, 'Test Project Description')
    
    def test_project_create_view(self):
        """Тест для проверки создания проекта"""
        project_count = Project.objects.count()
        response = self.client.post(reverse('project_create'), {
            'name': 'New Test Project',
            'description': 'New Test Project Description',
        })
        # Проверяем, что произошел редирект после успешного создания
        self.assertEqual(response.status_code, 302)
        # Проверяем, что проект был создан
        self.assertEqual(Project.objects.count(), project_count + 1)
        # Проверяем, что проект создан с правильными данными
        new_project = Project.objects.latest('id')
        self.assertEqual(new_project.name, 'New Test Project')
        self.assertEqual(new_project.description, 'New Test Project Description')
        self.assertEqual(new_project.owner, self.user)
    
    def test_project_update_view(self):
        """Тест для проверки обновления проекта"""
        response = self.client.post(reverse('project_update', args=[self.project.id]), {
            'name': 'Updated Test Project',
            'description': 'Updated Test Project Description',
        })
        # Проверяем, что произошел редирект после успешного обновления
        self.assertEqual(response.status_code, 302)
        # Проверяем, что проект был обновлен с правильными данными
        updated_project = Project.objects.get(id=self.project.id)
        self.assertEqual(updated_project.name, 'Updated Test Project')
        self.assertEqual(updated_project.description, 'Updated Test Project Description')
    
    def test_project_delete_view(self):
        """Тест для проверки удаления проекта"""
        project_count = Project.objects.count()
        response = self.client.post(reverse('project_delete', args=[self.project.id]))
        # Проверяем, что произошел редирект после успешного удаления
        self.assertEqual(response.status_code, 302)
        # Проверяем, что проект был удален
        self.assertEqual(Project.objects.count(), project_count - 1)
        # Проверяем, что проекта больше нет в базе данных
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=self.project.id)

class CategoryCRUDTestCase(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Создаем тестовую категорию
        self.category = Category.objects.create(
            name='Test Category'
        )
        
        # Создаем клиент для тестирования
        self.client = Client()
        
        # Авторизуем пользователя
        self.client.login(username='testuser', password='testpassword')
    
    def test_category_list_view(self):
        """Тест для проверки списка категорий"""
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_list.html')
        self.assertContains(response, 'Test Category')
    
    def test_category_create_view(self):
        """Тест для проверки создания категории"""
        category_count = Category.objects.count()
        response = self.client.post(reverse('category_create'), {
            'name': 'New Test Category'
        })
        # Проверяем, что произошел редирект после успешного создания
        self.assertEqual(response.status_code, 302)
        # Проверяем, что категория была создана
        self.assertEqual(Category.objects.count(), category_count + 1)
        # Проверяем, что категория создана с правильными данными
        new_category = Category.objects.latest('id')
        self.assertEqual(new_category.name, 'New Test Category')
    
    def test_category_update_view(self):
        """Тест для проверки обновления категории"""
        response = self.client.post(reverse('category_update', args=[self.category.id]), {
            'name': 'Updated Test Category'
        })
        # Проверяем, что произошел редирект после успешного обновления
        self.assertEqual(response.status_code, 302)
        # Проверяем, что категория была обновлена с правильными данными
        updated_category = Category.objects.get(id=self.category.id)
        self.assertEqual(updated_category.name, 'Updated Test Category')
    
    def test_category_delete_view(self):
        """Тест для проверки удаления категории"""
        category_count = Category.objects.count()
        response = self.client.post(reverse('category_delete', args=[self.category.id]))
        # Проверяем, что произошел редирект после успешного удаления
        self.assertEqual(response.status_code, 302)
        # Проверяем, что категория была удалена
        self.assertEqual(Category.objects.count(), category_count - 1)
        # Проверяем, что категории больше нет в базе данных
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=self.category.id)
