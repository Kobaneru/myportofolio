from django.urls import path

from main.views import show_main, show_experience, show_education, create_experience, get_experiences_json, delete_experience, create_education, create_education_ajax, get_educations_json, delete_education, update_education, update_education_ajax, register, login_user, logout_user, toggle_experience_star, toggle_education_star, show_favorites, show_json, show_json_by_id, create_experience_ajax, delete_experience_ajax, update_experience_ajax

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("experience/add/", create_experience, name="create_experience"),
    path("api/experience/", get_experiences_json, name="get_experiences_json"),
    path("experience/json/", show_json, name="show_json"),
    path("experience/json/<uuid:id>/", show_json_by_id, name="show_json_by_id"),
    path("experience/add-ajax/", create_experience_ajax, name="create_experience_ajax"),
    path("experience/delete-ajax/<uuid:id>/", delete_experience_ajax, name="delete_experience_ajax"),
    path("experience/update-ajax/<uuid:id>/", update_experience_ajax, name="update_experience_ajax"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("education/add/", create_education, name="create_education"),
    path("education/add-ajax/", create_education_ajax, name="create_education_ajax"),
    path("education/update-ajax/<uuid:education_id>/", update_education_ajax, name="update_education_ajax"),
    path("api/education/", get_educations_json, name="get_educations_json"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),
    path("education/<uuid:education_id>/update/", update_education, name="update_education"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path(
        "experience/<uuid:experience_id>/star/",
        toggle_experience_star,
        name="toggle_experience_star",
    ),
    path(
        "education/<uuid:education_id>/star/",
        toggle_education_star,
        name="toggle_education_star",
    ),
    path('favorites/', show_favorites, name='show_favorites'),
]