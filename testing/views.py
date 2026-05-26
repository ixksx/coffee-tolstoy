from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import Test, TestAttempt, UserAnswer
from training.models import Module


@login_required
def test_start_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    test = get_object_or_404(Test, module=module)
    user = request.user

    if not user.is_admin:
        from training.models import Program
        program = Program.objects.filter(role=user.role).first()
        if not program or module.program != program:
            return redirect('training:modules')

    attempts = TestAttempt.objects.filter(user=user, test=test, is_completed=True)
    attempt_count = attempts.count()

    active_attempt = TestAttempt.objects.filter(
        user=user, test=test, is_completed=False
    ).first()

    is_locked = False
    locked_until = None
    if attempt_count >= 2:
        last_attempt = attempts.order_by('-completed_at').first()
        if last_attempt and not last_attempt.is_passed:
            # Проверяем, прошла ли неделя с последней попытки
            lock_date = last_attempt.completed_at + timedelta(weeks=1)
            if timezone.now() < lock_date:
                is_locked = True
                locked_until = lock_date
            else:
                pass

    is_already_passed = attempts.filter(is_passed=True).exists()

    context = {
        'module': module,
        'test': test,
        'attempts': attempts,
        'attempt_count': attempt_count,
        'is_locked': is_locked,
        'locked_until': locked_until,
        'is_already_passed': is_already_passed,
        'active_attempt': active_attempt,
    }
    return render(request, 'testing/test_start.html', context)


@login_required
def test_take_view(request, module_id):

    module = get_object_or_404(Module, id=module_id)
    test = get_object_or_404(Test, module=module)
    user = request.user


    if not user.is_admin:
        from training.models import Program
        program = Program.objects.filter(role=user.role).first()
        if not program or module.program != program:
            return redirect('training:modules')


    completed_attempts = TestAttempt.objects.filter(
        user=user, test=test, is_completed=True
    )
    if completed_attempts.count() >= 2:
        last = completed_attempts.order_by('-completed_at').first()
        if last and not last.is_passed:
            lock_date = last.completed_at + timedelta(weeks=1)
            if timezone.now() < lock_date:
                messages.error(request, 'Тест заблокирован. Попробуйте позже.')
                return redirect('testing:test_start', module_id=module_id)


    active_attempt = TestAttempt.objects.filter(
        user=user, test=test, is_completed=False
    ).first()

    if not active_attempt:
        attempt_number = completed_attempts.count() + 1
        active_attempt = TestAttempt.objects.create(
            user=user,
            test=test,
            attempt_number=attempt_number,
        )

    questions = test.questions.all().order_by('order')

    if request.method == 'POST':

        correct_count = 0
        total = questions.count()

        for question in questions:
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                try:
                    selected_answer = question.answers.get(id=answer_id)
                    is_correct = selected_answer.is_correct
                    if is_correct:
                        correct_count += 1
                    UserAnswer.objects.update_or_create(
                        attempt=active_attempt,
                        question=question,
                        defaults={
                            'selected_answer': selected_answer,
                            'is_correct': is_correct,
                        }
                    )
                except Exception:
                    pass


        score = (correct_count / total * 100) if total > 0 else 0
        active_attempt.score = round(score, 1)
        active_attempt.total_questions = total
        active_attempt.correct_answers = correct_count
        active_attempt.is_passed = score >= 80
        active_attempt.is_completed = True
        active_attempt.completed_at = timezone.now()


        if not active_attempt.is_passed and active_attempt.attempt_number >= 2:
            active_attempt.locked_until = timezone.now() + timedelta(weeks=1)

        active_attempt.save()

        return redirect('testing:test_result', attempt_id=active_attempt.id)

    context = {
        'module': module,
        'test': test,
        'questions': questions,
        'attempt': active_attempt,
    }
    return render(request, 'testing/test_take.html', context)


@login_required
def test_result_view(request, attempt_id):

    attempt = get_object_or_404(TestAttempt, id=attempt_id)

    if attempt.user != request.user and not request.user.is_admin:
        return redirect('training:modules')

    user_answers = attempt.user_answers.select_related(
        'question', 'selected_answer'
    ).all()

    context = {
        'attempt': attempt,
        'user_answers': user_answers,
    }
    return render(request, 'testing/test_result.html', context)
