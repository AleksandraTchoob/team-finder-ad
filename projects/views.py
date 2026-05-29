from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProjectForm
from .models import Project
from users.utils import get_paginated_queryset


PROJECT_STATUS_OPEN = "open"
PROJECT_STATUS_CLOSED = "closed"


def project_list_view(request):
    """Главная страница."""
    projects = Project.objects.select_related("owner").all()

    page_obj = get_paginated_queryset(projects, request)

    return render(
        request,
        "projects/project_list.html",
        {
            "page_obj": page_obj,
        },
    )


def project_detail_view(request, pk):
    """Страница проекта."""
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"), pk=pk
    )

    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    """Создание проекта."""
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            # Автор автоматически становится участником
            project.participants.add(request.user)
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def edit_project_view(request, pk):
    """Редактирование проекта."""
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": True,
            "project": project,  # Добавляем для кнопки "Отмена"
        },
    )


@login_required
def complete_project_view(request, pk):
    """Завершение проекта."""
    project = Project.objects.filter(pk=pk, owner=request.user).first()

    if not project:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден или у вас нет прав на управление"},
            status=HTTPStatus.NOT_FOUND
        )

    if request.method == "POST":
        if project.status == PROJECT_STATUS_OPEN:
            project.status = PROJECT_STATUS_CLOSED
            project.save()
            return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})

    return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)


@login_required
def toggle_participate_view(request, pk):
    """Присоединиться/отказаться от участия в проекте."""
    project = Project.objects.filter(pk=pk).first()

    if not project:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND
        )

    if request.method == "POST":
        is_participating = project.participants.filter(pk=request.user.pk).exists()
        if is_participating:
            project.participants.remove(request.user)
        else:
            project.participants.add(request.user)

        return JsonResponse({"status": "ok", "is_participating": not is_participating})

    return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)


@login_required
def toggle_favorite_view(request, pk):
    """Добавить/удалить проект из избранного (Вариант 1)."""
    project = Project.objects.filter(pk=pk).first()

    if not project:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND
        )

    if request.method == "POST":
        is_favorited = project.interested_users.filter(pk=request.user.pk).exists()
        if is_favorited:
            project.interested_users.remove(request.user)
        else:
            project.interested_users.add(request.user)

        return JsonResponse({"status": "ok", "favorited": not is_favorited})

    return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)


@login_required
def favorite_projects_view(request):
    """Страница избранных проектов (Вариант 1)."""
    projects = request.user.favorites.select_related("owner").all()

    page_obj = get_paginated_queryset(projects, request)

    return render(request, "projects/favorite_projects.html", {"projects": page_obj})
