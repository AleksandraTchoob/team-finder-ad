from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Project
from .forms import ProjectForm


def project_list_view(request):
    """Главная страница."""
    projects = Project.objects.select_related("owner").all()

    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

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
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "POST":
        if project.status == "open":
            project.status = "closed"
            project.save()
            return JsonResponse({"status": "ok", "project_status": "closed"})

    return JsonResponse({"status": "error"}, status=400)


@login_required
def toggle_participate_view(request, pk):
    """Присоединиться/отказаться от участия в проекте."""
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        if request.user in project.participants.all():
            project.participants.remove(request.user)
            is_participating = False
        else:
            project.participants.add(request.user)
            is_participating = True

        return JsonResponse({"status": "ok", "is_participating": is_participating})

    return JsonResponse({"status": "error"}, status=400)


@login_required
def toggle_favorite_view(request, pk):
    """Добавить/удалить проект из избранного (Вариант 1)."""
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        if request.user in project.interested_users.all():
            project.interested_users.remove(request.user)
            is_favorited = False
        else:
            project.interested_users.add(request.user)
            is_favorited = True

        return JsonResponse({"status": "ok", "favorited": is_favorited})

    return JsonResponse({"status": "error"}, status=400)


@login_required
def favorite_projects_view(request):
    """Страница избранных проектов (Вариант 1)."""
    projects = request.user.favorites.select_related("owner").all()

    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "projects/favorite_projects.html", {"projects": page_obj})
