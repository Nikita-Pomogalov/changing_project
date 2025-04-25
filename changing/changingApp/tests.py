from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Announcement
from .forms import UserCreationForm, LoginForm, AnnouncementForm
from django.core.files.uploadedfile import SimpleUploadedFile
User = get_user_model()


class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.test_user = {
            'username': 'testuser',
            'password1': 'Testpass123',
            'password2': 'Testpass123'
        }

    # Тесты регистрации
    def test_user_registration_view(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], UserCreationForm)

    def test_successful_user_registration(self):
        response = self.client.post(self.register_url, self.test_user, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertRedirects(response, reverse('main'))

    def test_password_mismatch_registration(self):
        data = self.test_user.copy()
        data['password2'] = 'Wrongpass123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    # Тесты авторизации
    def test_user_login_view(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIsInstance(response.context['form'], LoginForm)

    def test_successful_user_login(self):
        User.objects.create_user(username='testuser', password='Testpass123')
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'Testpass123'
        }, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('main'))

    def test_failed_user_login(self):
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)


class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(self.user)

    def test_announcement_form_valid(self):
        form_data = {
            'title': 'Test Announcement',
            'description': 'Test description',
            'category': 'Test category',
            'condition': 'new'
        }
        form = AnnouncementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_announcement_form_invalid(self):
        form_data = {
            'title': '',  # Пустое поле
            'description': 'Test description',
            'category': 'Test category',
            'condition': 'invalid'  # Неверный выбор
        }
        form = AnnouncementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)  # Ожидаем 2 ошибки

    def test_announcement_creation(self):
        create_url = reverse('create_an')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AnnouncementForm)

        valid_jpeg = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
            b'\xff\xdb\x00C\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04'
            b'\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0c'
            b'\n\x0c\x0c\x0b\n\x0b\x0b\r\x0e\x12\x10\r\x0e\x11\x0e\x0b\x0b'
            b'\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14'
            b'\x18\x12\x14\x15\x14\xff\xdb\x00C\x01\x03\x04\x04\x05\x04\x05'
            b'\t\x05\x05\t\x14\r\x0b\r\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\xff\xc0\x00\x0b\x08\x00\x01'
            b'\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc4\x00'
            b'\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xd2\xcf'
            b'\xff\xd9'
        )

        test_image = SimpleUploadedFile(
            "test.jpg",
            content=valid_jpeg,
            content_type="image/jpeg"
        )

        response = self.client.post(create_url, {
            'title': 'Test Title',
            'description': 'Test Description',
            'category': 'Test Category',
            'condition': 'Новый',
            'image': test_image
        }, follow=True)

        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Announcement.objects.filter(title='Test Title').exists())
        announcement = Announcement.objects.first()
        self.assertEqual(announcement.user, self.user)