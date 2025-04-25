from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Announcement
from .forms import AnnouncementForm, LoginForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import psycopg2


def main_page(request):
    return render(request, 'base.html')

@login_required
def my_announcements(request):
    # Получаем объявления только текущего пользователя
    announcements = Announcement.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'all_an.html', {'announcements': announcements})

@login_required
def create_an(request):  # Убрали параметр an_id
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.user = request.user
            announcement.save()
            messages.success(request, 'Объявление успешно создано!')
            return redirect('all_an')
    else:
        form = AnnouncementForm()
    return render(request, 'create_an.html', {'form': form})


@login_required
def update_an(request, an_id):
    an = get_object_or_404(Announcement, id=an_id)
    if an.user != request.user:
        return redirect('main')

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=an)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление успешно обновлено!')
            return redirect('all_an')

    else:
        form = AnnouncementForm(instance=an)
    return render(request, 'update_an.html', { 'form': form })

@login_required
def delete_an(request, an_id):
    an = get_object_or_404(Announcement, id=an_id)
    if an.user == request.user:
        an.delete()
        messages.error(request, 'Объявление было удалено!')
    return redirect('all_an')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print("Form data:", request.POST)  # Что реально пришло
        print("Form is valid:", form.is_valid())  # Результат валидации
        print("Form errors:", form.errors)  # Ошибки
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('main')
        else:
            # Добавляем конкретные ошибки полей
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('main')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        print("Form data:", request.POST)  # Что реально пришло
        print("Form is valid:", form.is_valid())  # Результат валидации
        print("Form errors:", form.errors)  # Ошибки

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {user.username}!")
                next_url = request.POST.get('next') or request.GET.get('next') or 'main'
                return redirect(next_url)
            else:
                messages.error(request, 'Неверные учетные данные. Попробуйте снова.')
        else:
            # Детализируем ошибки валидации
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = LoginForm()

    return render(request, 'login.html', {
        'form': form,
        'next': request.GET.get('next', '')  # Для передачи next-параметра
    })



# Create your views here.
