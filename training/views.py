
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Program, Module, Lesson, LessonProgress
from .serializers import ModuleCardSerializer, LessonCardSerializer


@login_required
def about_view(request):
    benefits = [
        {
            'title': 'Профессиональный рост',
            'description': 'Развивайте навыки и становитесь экспертом в своём деле.',
            'icon': 'images/1.jpg',
        },
        {
            'title': 'Гибкий график обучения',
            'description': 'Учитесь в удобное время, материалы доступны 24/7.',
            'icon': 'images/2.jpg',
        },
        {
            'title': 'Практика с первого дня',
            'description': 'Каждый урок закрепляется реальной практикой на рабочем месте.',
            'icon': 'images/3.jpg',
        },
        {
            'title': 'Поддержка наставников',
            'description': 'Опытные менеджеры всегда готовы помочь и направить.',
            'icon': 'images/4.jpg',
        },
        {
            'title': 'Карьерные возможности',
            'description': 'Завершите программу и откройте путь к повышению.',
            'icon': 'images/5.jpg',
        },
    ]
    return render(request, 'training/about.html', {'benefits': benefits})


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def modules_view(request):
    
    user = request.user
    sort = request.GET.get('sort', 'newest') 

    if user.is_admin:
        programs = Program.objects.all()
        selected_program_id = request.GET.get('program')
        if selected_program_id:
            modules = Module.objects.filter(program_id=selected_program_id)
        else:
            modules = Module.objects.all()
    else:

        programs = None
        program = Program.objects.filter(role=user.role).first()
        if program:
            modules = program.modules.all()
        else:
            modules = Module.objects.none()

    modules_with_progress = []
    for module in modules:
        total = module.lessons.count()
        completed = LessonProgress.objects.filter(
            user=user, lesson__module=module, completed=True
        ).count() if not user.is_admin else 0
        percent = int(completed / total * 100) if total > 0 else 0
        modules_with_progress.append({
            'module': module,
            'total_lessons': total,
            'completed_lessons': completed,
            'percent': percent,
        })

    # Пагинация
    paginator = Paginator(modules_with_progress, 3)
    page = request.GET.get('page')
    try:
        modules_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        modules_page = paginator.page(1)

    context = {
        'modules': modules_page,
        'sort': sort,
        'programs': programs,
        'page_obj': modules_page,
    }
    return render(request, 'training/modules.html', context)


@login_required
def module_detail_view(request, module_id):

    module = get_object_or_404(Module, id=module_id)

    user = request.user
    if not user.is_admin:
        program = Program.objects.filter(role=user.role).first()
        if not program or module.program != program:
            return redirect('training:modules')

    lessons = module.lessons.all().order_by('number')

    lessons_with_progress = []
    for lesson in lessons:
        progress = LessonProgress.objects.filter(
            user=user, lesson=lesson
        ).first()
        lessons_with_progress.append({
            'lesson': lesson,
            'completed': progress.completed if progress else False,
        })

    # Пагинация
    paginator = Paginator(lessons_with_progress, 6)
    page = request.GET.get('page')
    try:
        lessons_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        lessons_page = paginator.page(1)

    context = {
        'module': module,
        'lessons': lessons_page,
        'page_obj': lessons_page,
    }
    return render(request, 'training/module_detail.html', context)


@login_required
def lesson_detail_view(request, lesson_id):

    lesson = get_object_or_404(Lesson, id=lesson_id)
    user = request.user


    if not user.is_admin:
        program = Program.objects.filter(role=user.role).first()
        if not program or lesson.module.program != program:
            return redirect('training:modules')

    if request.method == 'POST' and 'complete_lesson' in request.POST:
        progress, created = LessonProgress.objects.get_or_create(
            user=user, lesson=lesson
        )
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        return redirect('training:lesson_detail', lesson_id=lesson.id)


    progress = LessonProgress.objects.filter(user=user, lesson=lesson).first()


    from .models import PracticeGrade
    practice_grade = PracticeGrade.objects.filter(user=user, lesson=lesson).first()

    context = {
        'lesson': lesson,
        'files': lesson.files.all(),
        'images': lesson.images.all(),
        'progress': progress,
        'practice_grade': practice_grade,
    }
    return render(request, 'training/lesson_detail.html', context)


# API endpoints для AJAX пагинации
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_modules_list(request):
    user = request.user
    program_id = request.GET.get('program')
    page = request.GET.get('page', 1)

    if user.is_admin:
        if program_id:
            modules = Module.objects.filter(program_id=program_id)
        else:
            modules = Module.objects.all()
    else:
        program = Program.objects.filter(role=user.role).first()
        if program:
            modules = program.modules.all()
        else:
            modules = Module.objects.none()

    modules_data = []
    for idx, module in enumerate(modules, start=1):
        total = module.lessons.count()
        completed = LessonProgress.objects.filter(
            user=user, lesson__module=module, completed=True
        ).count() if not user.is_admin else 0
        percent = int(completed / total * 100) if total > 0 else 0
        modules_data.append({
            'id': module.id,
            'name': module.name,
            'description': module.description,
            'image': module.image.url if module.image else None,
            'total_lessons': total,
            'completed_lessons': completed,
            'percent': percent,
            'number': idx,
        })

    paginator = Paginator(modules_data, 3)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return JsonResponse({
        'modules': page_obj.object_list,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'current_page': page_obj.number,
        'num_pages': paginator.num_pages,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_lessons_list(request, module_id):
    user = request.user
    page = request.GET.get('page', 1)

    module = get_object_or_404(Module, id=module_id)

    if not user.is_admin:
        program = Program.objects.filter(role=user.role).first()
        if not program or module.program != program:
            return JsonResponse({'error': 'Access denied'}, status=403)

    lessons = module.lessons.all().order_by('number')

    lessons_data = []
    for lesson in lessons:
        progress = LessonProgress.objects.filter(user=user, lesson=lesson).first()
        lessons_data.append({
            'id': lesson.id,
            'number': lesson.number,
            'title': lesson.title,
            'image': lesson.image.url if lesson.image else None,
            'completed': progress.completed if progress else False,
        })

    paginator = Paginator(lessons_data, 6)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return JsonResponse({
        'lessons': page_obj.object_list,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'current_page': page_obj.number,
        'num_pages': paginator.num_pages,
    })
