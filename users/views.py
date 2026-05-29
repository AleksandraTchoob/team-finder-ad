from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import RegistrationForm, LoginForm, EditProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from .models import User


def register_view(request):
    """Страница регистрации."""
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/projects/list/")
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
                return redirect("/projects/list/")
            else:
                form.add_error(None, "Неверный email или пароль!")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    """Выход из аккаунта."""
    logout(request)
    return redirect("/projects/list/")


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
    participants = User.objects.filter(is_active=True).order_by("-date_joined")

    # Фильтрация (для Варианта 1)
    filter_type = request.GET.get("filter")
    active_filter = filter_type if filter_type else ""

    if request.user.is_authenticated and filter_type:
        if filter_type == "owners-of-favorite-projects":
            # Авторы избранных проектов текущего пользователя
            participants = participants.filter(
                owned_projects__in=request.user.favorites.all()
            ).distinct()
        elif filter_type == "owners-of-participating-projects":
            # Авторы проектов, в которых я участвую
            participants = participants.filter(
                owned_projects__participants=request.user
            ).distinct()
        elif filter_type == "interested-in-my-projects":
            # Пользователи, которым нравятся мои проекты
            participants = participants.filter(
                favorites__in=request.user.owned_projects.all()
            ).distinct()
        elif filter_type == "participants-of-my-projects":
            # Участники моих проектов
            participants = participants.filter(
                participated_projects__in=request.user.owned_projects.all()
            ).distinct()

    paginator = Paginator(participants, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "users/participants.html",
        {"page_obj": page_obj, "active_filter": active_filter},
    )
