
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from accounts.models import User
from training.models import (
    Program, Module, Lesson, LessonFile, LessonImage,
    LessonProgress, PracticeGrade
)
from testing.models import Test, Question, Answer, TestAttempt


def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, 'Доступ запрещён.')
            return redirect('training:about')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@admin_required
def dashboard_index(request):
    total_employees = User.objects.exclude(role='admin').exclude(is_superuser=True).count()
    total_programs = Program.objects.count()
    total_modules = Module.objects.count()
    total_lessons = Lesson.objects.count()

    avg_score = TestAttempt.objects.filter(
        is_completed=True
    ).aggregate(avg=Avg('score'))['avg'] or 0


    employees = User.objects.exclude(role='admin').exclude(is_superuser=True)
    completed_count = 0
    for emp in employees:
        program = Program.objects.filter(role=emp.role).first()
        if program:
            total = Lesson.objects.filter(module__program=program).count()
            done = LessonProgress.objects.filter(
                user=emp, completed=True, lesson__module__program=program
            ).count()
            if total > 0 and done >= total:
                completed_count += 1


    recent_attempts = TestAttempt.objects.filter(
        is_completed=True
    ).order_by('-completed_at')[:10]

    context = {
        'total_employees': total_employees,
        'total_programs': total_programs,
        'total_modules': total_modules,
        'total_lessons': total_lessons,
        'avg_score': round(avg_score, 1),
        'completed_count': completed_count,
        'recent_attempts': recent_attempts,
    }
    return render(request, 'dashboard/index.html', context)


@admin_required
def employee_list(request):

    employees = User.objects.exclude(role='admin').exclude(
        is_superuser=True
    ).order_by('last_name')
    return render(request, 'dashboard/employee_list.html', {'employees': employees})


@admin_required
def employee_detail(request, user_id):
    employee = get_object_or_404(User, id=user_id)
    program = Program.objects.filter(role=employee.role).first()

    # Прогресс по модулям
    modules_progress = []
    if program:
        for module in program.modules.all().order_by('order'):
            total = module.lessons.count()
            done = LessonProgress.objects.filter(
                user=employee, lesson__module=module, completed=True
            ).count()
            percent = int(done / total * 100) if total > 0 else 0
            # Попытки теста по модулю
            test_attempts = TestAttempt.objects.filter(
                user=employee, test__module=module
            ).order_by('attempt_number')
            modules_progress.append({
                'module': module,
                'total': total,
                'done': done,
                'percent': percent,
                'test_attempts': test_attempts,
            })

    # Оценки за практику
    practice_grades = PracticeGrade.objects.filter(user=employee).order_by('-graded_at')

    context = {
        'employee': employee,
        'program': program,
        'modules_progress': modules_progress,
        'practice_grades': practice_grades,
    }
    return render(request, 'dashboard/employee_detail.html', context)


@admin_required
def employee_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', 'trainee_barista')
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Логин и пароль обязательны.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким логином уже существует.')
        else:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=role,
                must_change_password=True,
            )
            messages.success(
                request,
                f'Сотрудник {user.get_full_name()} создан. '
                f'Логин: {username}, временный пароль: {password}'
            )
            return redirect('dashboard:employee_list')

    roles = User.ROLE_CHOICES
    return render(request, 'dashboard/employee_create.html', {'roles': roles})


@admin_required
def employee_edit(request, user_id):
    employee = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        employee.first_name = request.POST.get('first_name', '')
        employee.last_name = request.POST.get('last_name', '')
        employee.role = request.POST.get('role', employee.role)
        employee.email = request.POST.get('email', '')
        employee.phone = request.POST.get('phone', '')
        new_password = request.POST.get('new_password', '').strip()
        if new_password:
            employee.set_password(new_password)
            employee.must_change_password = True
        employee.save()
        messages.success(request, 'Данные сотрудника обновлены.')
        return redirect('dashboard:employee_detail', user_id=user_id)

    roles = User.ROLE_CHOICES
    return render(request, 'dashboard/employee_edit.html', {
        'employee': employee,
        'roles': roles,
    })


@admin_required
def employee_delete(request, user_id):
    employee = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        name = employee.get_full_name()
        employee.delete()
        messages.success(request, f'Сотрудник {name} удалён.')
        return redirect('dashboard:employee_list')
    return render(request, 'dashboard/employee_delete.html', {'employee': employee})


@admin_required
def program_list(request):
    programs = Program.objects.all()
    paginator = Paginator(programs, 6)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    return render(request, 'dashboard/program_list.html', {'programs': page_obj, 'page_obj': page_obj})


@admin_required
def program_edit(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    if request.method == 'POST':
        program.name = request.POST.get('name', program.name)
        program.description = request.POST.get('description', '')
        program.order = request.POST.get('order', program.order)
        if 'image' in request.FILES:
            program.image = request.FILES['image']
        program.save()
        messages.success(request, 'Программа обновлена.')
        return redirect('dashboard:program_list')
    return render(request, 'dashboard/program_edit.html', {'program': program})


@admin_required
def module_create(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    if request.method == 'POST':
        module = Module.objects.create(
            program=program,
            name=request.POST.get('name', ''),
            description=request.POST.get('description', ''),
            goal=request.POST.get('goal', ''),
            order=request.POST.get('order', 0),
            image=request.FILES.get('image'),
        )
        messages.success(request, f'Модуль «{module.name}» создан.')
        return redirect('dashboard:program_edit', program_id=program_id)
    return render(request, 'dashboard/module_create.html', {'program': program})


@admin_required
def module_edit(request, module_id):

    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        module.name = request.POST.get('name', module.name)
        module.description = request.POST.get('description', '')
        module.goal = request.POST.get('goal', '')
        module.order = request.POST.get('order', module.order)
        if 'image' in request.FILES:
            module.image = request.FILES['image']
        module.save()
        messages.success(request, 'Модуль обновлён.')
        return redirect('dashboard:module_edit', module_id=module_id)

    lessons = module.lessons.all().order_by('number')
    test = Test.objects.filter(module=module).first()
    return render(request, 'dashboard/module_edit.html', {
        'module': module,
        'lessons': lessons,
        'test': test,
    })


@admin_required
def module_delete(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    program_id = module.program.id
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Модуль удалён.')
        return redirect('dashboard:program_edit', program_id=program_id)
    return render(request, 'dashboard/module_delete.html', {'module': module})


@admin_required
def lesson_create(request, module_id):

    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        lesson = Lesson.objects.create(
            module=module,
            number=request.POST.get('number', 1),
            title=request.POST.get('title', ''),
            content=request.POST.get('content', ''),
            practice_task=request.POST.get('practice_task', ''),
            image=request.FILES.get('image'),
        )

        for f in request.FILES.getlist('files'):
            LessonFile.objects.create(lesson=lesson, title=f.name, file=f)
        for img in request.FILES.getlist('extra_images'):
            LessonImage.objects.create(lesson=lesson, image=img)

        messages.success(request, f'Урок «{lesson.title}» создан.')
        return redirect('dashboard:module_edit', module_id=module_id)
    return render(request, 'dashboard/lesson_create.html', {'module': module})


@admin_required
def lesson_edit(request, lesson_id):
    """Редактирование урока."""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        lesson.number = request.POST.get('number', lesson.number)
        lesson.title = request.POST.get('title', lesson.title)
        lesson.content = request.POST.get('content', lesson.content)
        lesson.practice_task = request.POST.get('practice_task', '')
        if 'image' in request.FILES:
            lesson.image = request.FILES['image']
        lesson.save()

        for f in request.FILES.getlist('files'):
            LessonFile.objects.create(lesson=lesson, title=f.name, file=f)
        for img in request.FILES.getlist('extra_images'):
            LessonImage.objects.create(lesson=lesson, image=img)

        messages.success(request, 'Урок обновлён.')
        return redirect('dashboard:lesson_edit', lesson_id=lesson_id)

    files = lesson.files.all()
    images = lesson.images.all()
    return render(request, 'dashboard/lesson_edit.html', {
        'lesson': lesson,
        'files': files,
        'images': images,
    })


@admin_required
def lesson_file_delete(request, file_id):
    """Удаление файла урока."""
    lesson_file = get_object_or_404(LessonFile, id=file_id)
    lesson_id = lesson_file.lesson.id
    lesson_file.delete()
    messages.success(request, 'Файл удалён.')
    return redirect('dashboard:lesson_edit', lesson_id=lesson_id)


@admin_required
def lesson_image_delete(request, image_id):
    """Удаление изображения урока."""
    lesson_image = get_object_or_404(LessonImage, id=image_id)
    lesson_id = lesson_image.lesson.id
    lesson_image.delete()
    messages.success(request, 'Изображение удалено.')
    return redirect('dashboard:lesson_edit', lesson_id=lesson_id)


@admin_required
def lesson_delete(request, lesson_id):
    """Удаление урока."""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    module_id = lesson.module.id
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Урок удалён.')
        return redirect('dashboard:module_edit', module_id=module_id)
    return render(request, 'dashboard/lesson_delete.html', {'lesson': lesson})


@admin_required
def test_edit(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    test, created = Test.objects.get_or_create(
        module=module,
        defaults={'title': f'Тест: {module.name}'}
    )
    if request.method == 'POST':
        test.title = request.POST.get('title', test.title)
        test.description = request.POST.get('description', '')
        test.time_limit_minutes = request.POST.get('time_limit', 30)
        test.save()
        messages.success(request, 'Тест обновлён.')
        return redirect('dashboard:test_edit', module_id=module_id)

    questions = test.questions.all().order_by('order')
    return render(request, 'dashboard/test_edit.html', {
        'module': module,
        'test': test,
        'questions': questions,
    })


@admin_required
def question_create(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    if request.method == 'POST':
        question = Question.objects.create(
            test=test,
            text=request.POST.get('text', ''),
            order=request.POST.get('order', 0),
        )
        for i in range(1, 7):
            answer_text = request.POST.get(f'answer_{i}', '').strip()
            if answer_text:
                is_correct = request.POST.get(f'correct_{i}') == 'on'
                Answer.objects.create(
                    question=question,
                    text=answer_text,
                    is_correct=is_correct,
                )
        messages.success(request, 'Вопрос добавлен.')
        return redirect('dashboard:test_edit', module_id=test.module.id)
    return render(request, 'dashboard/question_create.html', {'test': test})


@admin_required
def question_edit(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        question.text = request.POST.get('text', question.text)
        question.order = request.POST.get('order', question.order)
        question.save()
        question.answers.all().delete()
        for i in range(1, 7):
            answer_text = request.POST.get(f'answer_{i}', '').strip()
            if answer_text:
                is_correct = request.POST.get(f'correct_{i}') == 'on'
                Answer.objects.create(
                    question=question,
                    text=answer_text,
                    is_correct=is_correct,
                )
        messages.success(request, 'Вопрос обновлён.')
        return redirect('dashboard:test_edit', module_id=question.test.module.id)

    answers = question.answers.all()
    return render(request, 'dashboard/question_edit.html', {
        'question': question,
        'answers': answers,
    })


@admin_required
def question_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    module_id = question.test.module.id
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Вопрос удалён.')
        return redirect('dashboard:test_edit', module_id=module_id)
    return render(request, 'dashboard/question_delete.html', {'question': question})


@admin_required
def practice_grade_view(request, user_id, lesson_id):
    employee = get_object_or_404(User, id=user_id)
    lesson = get_object_or_404(Lesson, id=lesson_id)

    grade_obj = PracticeGrade.objects.filter(user=employee, lesson=lesson).first()

    if request.method == 'POST':
        grade_value = int(request.POST.get('grade', 0))
        comment = request.POST.get('comment', '')
        if 1 <= grade_value <= 10:
            PracticeGrade.objects.update_or_create(
                user=employee,
                lesson=lesson,
                defaults={
                    'grade': grade_value,
                    'comment': comment,
                    'graded_by': request.user,
                }
            )
            messages.success(request, 'Оценка выставлена.')
            return redirect('dashboard:employee_detail', user_id=user_id)
        else:
            messages.error(request, 'Оценка должна быть от 1 до 10.')

    return render(request, 'dashboard/practice_grade.html', {
        'employee': employee,
        'lesson': lesson,
        'grade_obj': grade_obj,
    })
