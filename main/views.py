from django.shortcuts import render

from main.models import Experience, Achievement


def show_main(request):
    context = {
        "name": "Jonathan Sebastian Sindhu",
        "npm": "2506619650",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Motivated Computer Science student with strong academic achievements and experience in competitive programming. Skilled in algorithms, problem-solving, and C++ programming, with proven accomplishments in national informatics competitions. Committed to excellence in Computer Science, demonstrating both technical expertise and leadership through tutoring and training activities."
        ),
        "achievement_list": Achievement.objects.all().order_by('-year'),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Jonathan Sebastian Sindhu",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)