from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EditProfileForm, LoginForm, RegistrationForm
from .models import User
from .utils import get_paginated_queryset


FILTER_OWNERS_OF_FAVORITES = "owners-of-favorite-projects"
FILTER_OWNERS_OF_PARTICIPATING = "owners-of-participating-projects"
FILTER_INTERESTED_IN_MY_PROJECTS = "interested-in-my-projects"
FILTER_PARTICIPANTS_OF_MY_PROJECTS = "participants-of-my-projects"


def register_view(request):
    """Страница регистрации."""
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:project_list")
    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """Страница входа."""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect("projects:project_list")
            else:
                form.add_error(None, "Неверный email или пароль!")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    """Выход из аккаунта."""
    logout(request)
    return redirect("projects:project_list")


def user_detail_view(request, pk):
    """Страница пользователя."""
    user = get_object_or_404(User.objects.prefetch_related("owned_projects"), pk=pk)

    projects = user.owned_projects.all()

    return render(
        request, "users/user-details.html", {"user": user, "projects": projects}
    )


@login_required
def edit_profile_view(request):
    """Редактирование профиля."""
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:user_detail", pk=request.user.pk)
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    """Смена пароля."""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Чтобы пользователь не разлогинился после смены пароля
            update_session_auth_hash(request, user)
            return redirect("users:user_detail", pk=request.user.pk)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "users/change_password.html", {"form": form})


def participants_list_view(request):
    """Страница со списком всех пользователей."""
    participants = User.objects.filter(is_active=True).prefetch_related("favorites").order_by("-date_joined")

    # Фильтрация (для Варианта 1)
    filter_type = request.GET.get("filter")
    active_filter = filter_type if filter_type else ""

    if request.user.is_authenticated and filter_type:
        if filter_type == FILTER_OWNERS_OF_FAVORITES:
            # Авторы избранных проектов текущего пользователя
            participants = participants.filter(
                owned_projects__in=request.user.favorites.all()
            ).distinct()
        elif filter_type == FILTER_OWNERS_OF_PARTICIPATING:
            # Авторы проектов, в которых я участвую
            participants = participants.filter(
                owned_projects__participants=request.user
            ).distinct()
        elif filter_type == FILTER_INTERESTED_IN_MY_PROJECTS:
            # Пользователи, которым нравятся мои проекты
            participants = participants.filter(
                favorites__in=request.user.owned_projects.all()
            ).distinct()
        elif filter_type == FILTER_PARTICIPANTS_OF_MY_PROJECTS:
            # Участники моих проектов
            participants = participants.filter(
                participated_projects__in=request.user.owned_projects.all()
            ).distinct()

    page_obj = get_paginated_queryset(participants, request)

    return render(
        request,
        "users/participants.html",
        {"page_obj": page_obj, "active_filter": active_filter},
    )
