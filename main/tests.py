from html.parser import HTMLParser

from django.test import Client, TestCase
from django.urls import reverse
from datetime import date

from django.contrib.auth.models import User

from main.models import Experience, Education


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
            started_at=date(2026, 8, 1),
        )
        self.education = Education.objects.create(
            institution_name="University of Indonesia",
            degree="Bachelor of Computer Science",
            description="Activities and societies: DDP-0 (Programming Fundamental), Business Development Intern at BEM Fasilkom UI",
            started_at=date(2025, 7, 1),
            ended_at=date(2029, 8, 1),
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        # Halaman kini memuat data lewat AJAX, jadi cek kontainer & endpoint JSON
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, reverse("api:experience-list"))

    def test_experience_json_endpoint(self):
        response = self.client.get(reverse("main:show_json"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)

        experience = data[0]
        self.assertEqual(experience["title"], self.experience.title)
        self.assertEqual(experience["description"], self.experience.description)
        self.assertEqual(experience["category"], "Part-Time")
        self.assertEqual(experience["started_at"], "August 2026")
        self.assertTrue(experience["is_ongoing"])

    def test_experience_json_by_id(self):
        response = self.client.get(
            reverse("main:show_json_by_id", args=[self.experience.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], str(self.experience.id))

    def test_empty_experience_json(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_completed_experience(self):
        self.experience.ended_at = date.today()
        self.experience.save()
        response = self.client.get(reverse("main:show_json"))

        self.assertFalse(self.experience.is_ongoing)
        experience = response.json()[0]
        self.assertFalse(experience["is_ongoing"])
        self.assertEqual(experience["ended_at"], date.today().strftime("%B %Y"))

    def test_education_page(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, reverse("api:education-list"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        data = self.client.get(reverse("main:get_educations_json")).json()
        education = data[0]["fields"]
        self.assertEqual(education["institution_name"], self.education.institution_name)
        self.assertEqual(education["degree"], self.education.degree)
        self.assertEqual(education["description"], self.education.description)
        self.assertEqual(education["started_at"], "2025-07-01")
        self.assertEqual(education["ended_at"], "2029-08-01")

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, 'id="empty"')
        self.assertEqual(self.client.get(reverse("main:get_educations_json")).json(), [])



class ExperienceAjaxTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", password="pass12345"
        )
        self.user = User.objects.create_user(username="budi", password="pass12345")
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
            started_at=date(2026, 8, 1),
        )

    def test_add_modal_only_rendered_for_superuser(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, 'id="experience-form"')
        self.assertContains(response, 'id="add-experience-modal"')

        self.client.logout()
        response = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(response, 'id="experience-form"')

    def test_json_exposes_edit_html_only_for_superuser(self):
        self.client.force_login(self.admin)
        data = self.client.get(reverse("main:show_json")).json()
        self.assertIn("js-update-experience-form", data[0]["edit_html"])
        self.assertIn(str(self.experience.id), data[0]["edit_html"])

        self.client.logout()
        data = self.client.get(reverse("main:show_json")).json()
        self.assertEqual(data[0]["edit_html"], "")

    def test_create_experience_ajax(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("main:create_experience_ajax"),
            {
                "title": "Research Intern",
                "description": "Membantu riset.",
                "category": "research",
                "started_at": "2026-01-01",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Experience.objects.filter(title="Research Intern").exists())

    def test_create_experience_ajax_reports_field_errors(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("main:create_experience_ajax"), {"title": ""}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])

    def test_update_experience_ajax(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("main:update_experience_ajax", args=[self.experience.id]),
            {
                "title": "Asisten Dosen",
                "description": "Diperbarui.",
                "category": "volunteer",
                "started_at": "2026-08-01",
                "ended_at": "2026-09-01",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen")
        self.assertEqual(self.experience.category, "volunteer")

    def test_update_experience_ajax_rejects_invalid_data(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("main:update_experience_ajax", args=[self.experience.id]),
            {"title": ""},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen PBP")

    def test_ajax_endpoints_reject_non_superuser(self):
        self.client.force_login(self.user)
        payload = {
            "title": "Nakal",
            "description": "x",
            "category": "research",
            "started_at": "2026-01-01",
        }

        self.assertEqual(
            self.client.post(
                reverse("main:create_experience_ajax"), payload
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                reverse("main:update_experience_ajax", args=[self.experience.id]),
                payload,
            ).status_code,
            403,
        )

    def test_ajax_endpoints_require_login(self):
        self.assertEqual(
            self.client.post(
                reverse("main:create_experience_ajax"), {"title": "x"}
            ).status_code,
            403,
        )

    def test_update_experience_ajax_returns_404_for_missing_id(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse(
                "main:update_experience_ajax",
                args=["00000000-0000-0000-0000-000000000000"],
            ),
            {"title": "Apa saja"},
        )

        self.assertEqual(response.status_code, 404)

    def test_xss_payload_is_escaped_in_server_rendered_html(self):
        payload = "<script>alert('xss')</script>"
        self.experience.title = payload
        self.experience.save()

        self.client.force_login(self.admin)
        item = self.client.get(reverse("main:show_json")).json()[0]

        # Auto-escaping Django mengubah payload menjadi entitas HTML,
        # sehingga tidak bisa dieksekusi sebagai tag <script>.
        for key in ("edit_html", "delete_html"):
            self.assertIn("&lt;script&gt;", item[key])
            self.assertNotIn(payload, item[key])

    def test_json_is_served_with_json_content_type(self):
        # Konten JSON tidak dirender sebagai HTML oleh browser.
        response = self.client.get(reverse("main:show_json"))
        self.assertEqual(response["Content-Type"], "application/json")

    def test_experience_template_escapes_dynamic_values(self):
        response = self.client.get(reverse("main:show_experience"))

        # escapeHtml() wajib dipakai untuk setiap nilai dinamis dari JSON.
        self.assertContains(response, "/static/js/portfolio.js")
        self.assertContains(response, "escapeHtml(experience.title)")
        self.assertContains(response, "escapeHtml(experience.description)")

    def test_drf_experience_create_update_and_delete(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("api:experience-list"), {
            "title": "DRF Intern", "description": "API integration",
            "category": "internship", "started_at": "2026-08-01", "ended_at": None,
        }, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        detail = reverse("api:experience-detail", args=[response.json()["id"]])
        response = self.client.patch(detail, {"title": "Updated Intern"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Updated Intern")
        self.assertIsNone(response.json()["ended_at"])
        response = self.client.delete(detail)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")

    def test_legacy_delete_route_uses_matching_view_parameter(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("main:delete_experience_ajax", args=[self.experience.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())


class _DeleteFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current_form = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.current_form = {"attrs": attrs, "fields": {}}
            self.forms.append(self.current_form)
        elif tag == "input" and self.current_form is not None and "name" in attrs:
            self.current_form["fields"][attrs["name"]] = attrs.get("value", "")

    def handle_endtag(self, tag):
        if tag == "form":
            self.current_form = None


class DeleteModalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(username="modal-owner")
        cls.experience = Experience.objects.create(
            title="Research", description="Description", category="research",
            started_at=date(2026, 1, 1),
        )
        cls.education = Education.objects.create(
            institution_name="School", started_at=date(2020, 1, 1), ended_at=date(2024, 1, 1),
        )

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)

    def test_ajax_pages_render_one_reusable_delete_modal(self):
        for resource in ("experience", "education"):
            with self.subTest(resource=resource):
                response = self.client.get(reverse(f"main:show_{resource}"))
                self.assertContains(response, f'id="delete-{resource}-modal"', count=1)
                self.assertContains(response, f'id="delete-{resource}-form"', count=1)
                self.assertContains(response, f'id="delete-{resource}-name"', count=1)

    def test_legacy_json_delete_forms_remain_usable_with_csrf(self):
        for resource, record, endpoint in (
            ("experience", self.experience, "main:show_json"),
            ("education", self.education, "main:get_educations_json"),
        ):
            with self.subTest(resource=resource):
                response = self.client.get(reverse(endpoint))
                self.assertEqual(response.status_code, 200)
                item = response.json()[0]
                markup = (item["fields"] if resource == "education" else item)["delete_html"]
                parser = _DeleteFormParser()
                parser.feed(markup)
                self.assertEqual(len(parser.forms), 1)
                form = parser.forms[0]
                self.assertEqual(form["attrs"]["method"], "post")
                self.assertEqual(form["attrs"]["action"], reverse(f"main:delete_{resource}", args=[record.id]))
                self.assertEqual(form["attrs"]["data-popover-id"], f"delete-{resource}-{record.id}")
                if resource == "experience":
                    self.assertIn("js-delete-experience-form", form["attrs"]["class"])
                self.assertIn("csrfmiddlewaretoken", form["fields"])
                response = self.client.post(form["attrs"]["action"], form["fields"])
                self.assertEqual(response.status_code, 302)
                self.assertFalse(type(record).objects.filter(pk=record.pk).exists())
