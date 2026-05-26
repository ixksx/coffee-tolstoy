from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q

from .forms import LoginForm, ForcePasswordChangeForm, ProfileEditForm
from training.models import Program, Module, Lesson, LessonProgress, PracticeGrade
from testing.models import TestAttempt


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('dashboard:index')
        return redirect('training:about')

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_admin:
                    return redirect('dashboard:index')
                return redirect('training:about')
            else:
                messages.error(request, 'Неверный логин или пароль.')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def force_change_password_view(request):

    form = ForcePasswordChangeForm()
    if request.method == 'POST':
        form = ForcePasswordChangeForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            if not request.user.check_password(old_password):
                messages.error(request, 'Старый пароль неверен.')
            else:
                request.user.set_password(new_password)
                request.user.must_change_password = False
                request.user.save()
                login(request, request.user)
                messages.success(request, 'Пароль успешно изменён!')
                return redirect('training:about')
    return render(request, 'accounts/force_change_password.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user


    if user.is_admin:
        return _admin_profile(request)


    program = Program.objects.filter(role=user.role).first()
    modules = []
    if program:
        for module in program.modules.all().order_by('order'):
            total_lessons = module.lessons.count()
            completed_lessons = LessonProgress.objects.filter(
                user=user, lesson__module=module, completed=True
            ).count()
            percent = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
            modules.append({
                'module': module,
                'total': total_lessons,
                'completed': completed_lessons,
                'percent': percent,
            })


    recent_tests = TestAttempt.objects.filter(user=user).order_by('-started_at')[:5]
    all_tests = TestAttempt.objects.filter(user=user).order_by('-started_at')

 
    practice_grades = PracticeGrade.objects.filter(user=user).order_by('-graded_at')

    context = {
        'program': program,
        'modules': modules,
        'recent_tests': recent_tests,
        'all_tests': all_tests,
        'practice_grades': practice_grades,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def _admin_profile(request):
    from accounts.models import User

    employees = User.objects.exclude(role='admin').exclude(is_superuser=True)
    total_employees = employees.count()

    completed_count = 0
    for emp in employees:
        program = Program.objects.filter(role=emp.role).first()
        if program:
            total_lessons = Lesson.objects.filter(module__program=program).count()
            completed_lessons = LessonProgress.objects.filter(
                user=emp, completed=True, lesson__module__program=program
            ).count()
            if total_lessons > 0 and completed_lessons >= total_lessons:
                completed_count += 1

  
    avg_score = TestAttempt.objects.filter(
        is_completed=True
    ).aggregate(avg=Avg('score'))['avg'] or 0

    context = {
        'employees': employees,
        'total_employees': total_employees,
        'completed_count': completed_count,
        'avg_score': round(avg_score, 1),
        'is_admin_profile': True,
    }
    return render(request, 'accounts/admin_profile.html', context)


@login_required
def profile_edit_view(request):
    form = ProfileEditForm(instance=request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('accounts:profile')
    return render(request, 'accounts/profile_edit.html', {'form': form})
