import uuid
from types import SimpleNamespace

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Experience
from main.serializers import EducationSerializer, ExperienceSerializer


class PortfolioAPITestMixin:
    """Kontrak API bersama untuk Experience dan Education."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        cls.visitor = User.objects.create_user(username="visitor", password="test-password")
        cls.editor = User.objects.create_user(username="editor")
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.record = cls.model.objects.create(**cls.initial_data)

    def setUp(self):
        self.list_url = reverse(f"api:{self.resource}-list")
        self.detail_url = reverse(f"api:{self.resource}-detail", args=[self.record.id])
        self.star_url = reverse(f"api:{self.resource}-star", args=[self.record.id])
        self.page_url = reverse(f"main:show_{self.resource}")

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        record = response.data[0]
        self.assertEqual(record["id"], str(self.record.id))
        for field, value in self.initial_data.items():
            self.assertEqual(record[field], value)
        self.assertEqual(record["star_count"], 0)
        self.assertFalse(record["is_starred"])
        self.assertEqual(record["starred_by_names"], "")
        self.assertEqual(set(record), set(self.initial_data) | {
            "id", "star_count", "is_starred", "starred_by_names",
        })
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, record)

    def test_search_and_empty_results(self):
        self.model.objects.create(**{**self.initial_data, self.name_field: "Unrelated entry"})
        response = self.client.get(self.list_url, {self.name_field: f"  {self.search_term.upper()}  "})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data], [str(self.record.id)])
        self.assertEqual(self.client.get(self.list_url, {self.name_field: "not-found"}).data, [])
        self.model.objects.all().delete()
        self.assertEqual(self.client.get(self.list_url).data, [])

    def test_missing_resource_returns_404(self):
        detail = reverse(f"api:{self.resource}-detail", args=[uuid.uuid4()])
        star = reverse(f"api:{self.resource}-star", args=[uuid.uuid4()])
        self.client.force_authenticate(user=self.owner)
        for method, url in (("get", detail), ("patch", detail), ("delete", detail), ("post", star)):
            with self.subTest(method=method):
                self.assertEqual(getattr(self.client, method)(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            for method, url, payload in (
                ("post", self.list_url, self.payload),
                ("put", self.detail_url, self.payload),
                ("patch", self.detail_url, {self.name_field: "Changed"}),
                ("delete", self.detail_url, None),
            ):
                with self.subTest(user=user, method=method):
                    response = getattr(self.client, method)(url, payload, format="json")
                    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.model.objects.count(), 1)
        self.record.refresh_from_db()
        self.assertEqual(getattr(self.record, self.name_field), self.initial_data[self.name_field])

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = self.model.objects.get(pk=response.data["id"])
        self.assertEqual(getattr(created, self.name_field), self.payload[self.name_field])
        self.assertEqual(created.description, self.payload["description"])
        self.assertEqual(self.model.objects.count(), 2)

    def test_validation_rejects_invalid_payloads(self):
        self.client.force_authenticate(user=self.owner)
        cases = [
            ({self.name_field: "   "}, self.name_field),
            ({self.name_field: '<img src="x" onerror="alert(1)">'}, self.name_field),
            ({"started_at": "invalid-date"}, "started_at"),
            ({"started_at": None}, "started_at"),
            *self.invalid_cases,
        ]
        for changes, field in cases:
            with self.subTest(changes=changes):
                response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        self.assertEqual(self.model.objects.count(), 1)

    def test_owner_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {self.name_field: "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.record.refresh_from_db()
        self.assertEqual(getattr(self.record, self.name_field), "Changed")
        self.assertEqual(self.record.description, self.initial_data["description"])
        response = self.client.put(self.detail_url, {self.name_field: "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.record.refresh_from_db()
        self.assertEqual(getattr(self.record, self.name_field), "Changed")
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.record.refresh_from_db()
        self.assertEqual(getattr(self.record, self.name_field), self.payload[self.name_field])
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(self.model.objects.filter(pk=self.record.id).exists())

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {self.name_field: "Editor update"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.record.refresh_from_db()
        self.assertEqual(getattr(self.record, self.name_field), "Editor update")
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.record.refresh_from_db()
        self.assertEqual(getattr(self.record, self.name_field), self.payload[self.name_field])
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(self.model.objects.count(), 1)

    def test_staff_without_editor_role_cannot_update(self):
        self.visitor.is_staff = True
        self.visitor.save(update_fields=["is_staff"])
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {self.name_field: "Denied"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.record.refresh_from_db()
        self.assertEqual(getattr(self.record, self.name_field), self.initial_data[self.name_field])

    def test_star_requires_login_and_toggles_for_current_user(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], self.visitor.username)
        self.assertTrue(self.record.starred_by.filter(pk=self.visitor.pk).exists())
        self.client.force_authenticate(user=self.editor)
        response = self.client.get(self.detail_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(self.client.post(self.star_url).data["star_count"], 2)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], self.editor.username)
        self.assertFalse(self.record.starred_by.filter(pk=self.visitor.pk).exists())

    def test_computed_fields_and_id_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        supplied_id = str(uuid.uuid4())
        response = self.client.post(self.list_url, {
            **self.payload, "id": supplied_id, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["id"], supplied_id)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertFalse(self.model.objects.get(pk=response.data["id"]).starred_by.exists())

    def test_wrong_methods_return_405(self):
        self.client.force_authenticate(user=self.owner)
        for method, url in (
            ("delete", self.list_url), ("patch", self.list_url),
            ("post", self.detail_url), ("get", self.star_url),
        ):
            with self.subTest(method=method, url=url):
                self.assertEqual(getattr(self.client, method)(url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.model.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        page = client.get(self.page_url)
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        headers = {"HTTP_X_CSRFTOKEN": client.cookies["csrftoken"].value}
        response = client.post(self.list_url, self.payload, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        detail = reverse(f"api:{self.resource}-detail", args=[response.data["id"]])
        response = client.patch(detail, {self.name_field: "Session update"}, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[self.name_field], "Session update")
        self.assertEqual(client.post(self.star_url, **headers).status_code, status.HTTP_200_OK)
        self.assertEqual(client.delete(detail, **headers).status_code, status.HTTP_204_NO_CONTENT)

    def test_date_range_validation_uses_saved_values_for_patch(self):
        self.client.force_authenticate(user=self.editor)
        original_start = self.initial_data["started_at"]
        response = self.client.patch(self.detail_url, {"ended_at": "2000-01-01"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("ended_at", response.data)
        self.record.refresh_from_db()
        self.assertEqual(self.record.started_at.isoformat(), original_start)
        self.assertEqual(
            self.record.ended_at.isoformat() if self.record.ended_at else None,
            self.initial_data["ended_at"],
        )
        # Same-day entries are valid. A later partial start-date change must
        # still compare against that end date, even when the client omits it.
        response = self.client.patch(self.detail_url, {"ended_at": original_start}, format="json")
        self.assertEqual(response.status_code, 200)
        response = self.client.patch(self.detail_url, {"started_at": "2100-01-01"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.record.refresh_from_db()
        self.assertEqual(self.record.started_at.isoformat(), original_start)
        self.assertEqual(self.record.ended_at.isoformat(), original_start)

    def test_list_star_queries_do_not_grow_with_entry_count(self):
        self.client.force_authenticate(user=self.visitor)
        self.record.starred_by.add(self.visitor)
        with self.assertNumQueries(2):
            response = self.client.get(self.list_url)
        self.assertEqual(response.data[0]["star_count"], 1)
        for index in range(4):
            record = self.model.objects.create(**{
                **self.initial_data, self.name_field: f"Additional entry {index}",
            })
            record.starred_by.add(self.visitor)
        with self.assertNumQueries(2):
            response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 5)
        self.assertTrue(all(item["is_starred"] and item["star_count"] == 1 for item in response.data))

    def test_unprefetched_serializer_reads_star_users_only_once(self):
        self.record.starred_by.add(self.visitor)
        serializer = self.serializer_class(self.record, context={
            "request": SimpleNamespace(user=self.visitor),
        })
        with self.assertNumQueries(1):
            data = serializer.data
        self.assertEqual(data["star_count"], 1)
        self.assertTrue(data["is_starred"])
        self.assertEqual(data["starred_by_names"], self.visitor.username)


    def test_editor_session_updates_and_page_includes_only_update_controls(self):
        self.client.force_login(self.editor)
        response = self.client.patch(self.detail_url, {self.name_field: "Session editor update"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.record.refresh_from_db()
        self.assertEqual(getattr(self.record, self.name_field), "Session editor update")
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.context["is_editor"])
        self.assertContains(response, f'id="{self.form_id}"')
        self.assertNotContains(response, f'class="button {self.resource}-add-button"')
        self.assertNotContains(response, f'id="delete-{self.resource}-modal"')

    def test_guest_and_visitor_pages_hide_write_forms(self):
        for user in (None, self.visitor):
            with self.subTest(user=user):
                self.client.logout()
                if user:
                    self.client.force_login(user)
                response = self.client.get(self.page_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertNotContains(response, f'id="{self.form_id}"')
                self.assertNotContains(response, f'id="add-{self.resource}-modal"')
                self.assertNotContains(response, f'id="delete-{self.resource}-modal"')

    def test_authenticated_star_requires_csrf_and_page_provides_token(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="visitor", password="test-password"))
        self.assertEqual(client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.record.starred_by.exists())
        page = client.get(self.page_url)
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertTrue(self.record.starred_by.filter(pk=self.visitor.pk).exists())


class ExperienceAPITest(PortfolioAPITestMixin, APITestCase):
    model = Experience
    serializer_class = ExperienceSerializer
    resource = "experience"
    form_id = "experience-form"
    name_field = "title"
    search_term = "research"
    initial_data = {
        "title": "Research Assistant", "description": "Membantu penelitian.",
        "category": "research", "thumbnail": "", "started_at": "2026-08-01", "ended_at": None,
    }
    payload = {
        "title": "Teaching Assistant", "description": "Membantu praktikum.",
        "category": "part-time", "thumbnail": "https://example.com/thumbnail.png",
        "started_at": "2026-01-01", "ended_at": "2026-06-01",
    }
    invalid_cases = [
        ({"category": "unknown-category"}, "category"),
        ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
        ({"ended_at": "2025-12-31"}, "ended_at"),
    ]

    def test_ongoing_experience_accepts_blank_thumbnail_and_null_end_date(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "thumbnail": "", "ended_at": None,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Experience.objects.get(pk=response.data["id"]).is_ongoing)
        self.assertIsNone(response.data["ended_at"])
        self.assertEqual(response.data["thumbnail"], "")



class EducationAPITest(PortfolioAPITestMixin, APITestCase):
    model = Education
    serializer_class = EducationSerializer
    resource = "education"
    form_id = "add-education-form"
    name_field = "institution_name"
    search_term = "indonesia"
    initial_data = {
        "institution_name": "Universitas Indonesia", "degree": "Ilmu Komputer",
        "description": "Pendidikan sarjana.", "started_at": "2025-07-01", "ended_at": "2029-08-01",
    }
    payload = {
        "institution_name": "New Institution", "degree": "Computer Science",
        "description": "Academic activities.", "started_at": "2020-01-01", "ended_at": "2024-01-01",
    }
    invalid_cases = [
        ({"ended_at": None}, "ended_at"),
        ({"ended_at": ""}, "ended_at"),
        ({"ended_at": "2019-12-31"}, "ended_at"),
    ]

    def test_partial_date_updates_validate_against_existing_dates(self):
        self.client.force_authenticate(user=self.editor)
        for changes in ({"ended_at": "2025-06-30"}, {"started_at": "2029-08-02"}):
            with self.subTest(changes=changes):
                response = self.client.patch(self.detail_url, changes, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("ended_at", response.data)
        self.record.refresh_from_db()
        self.assertEqual(self.record.started_at.isoformat(), self.initial_data["started_at"])
        self.assertEqual(self.record.ended_at.isoformat(), self.initial_data["ended_at"])
        response = self.client.patch(self.detail_url, {"ended_at": "2025-07-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_optional_degree_and_description_can_be_blank(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "degree": "", "description": "",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["degree"], "")
        self.assertEqual(response.data["description"], "")

    def test_optional_text_preserves_null_on_create_and_update(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "degree": None, "description": None,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        created = Education.objects.get(pk=response.data["id"])
        self.assertIsNone(created.degree)
        self.assertIsNone(created.description)
        self.assertIsNone(response.data["degree"])
        self.assertIsNone(response.data["description"])
        response = self.client.patch(self.detail_url, {
            "degree": None, "description": None,
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.record.refresh_from_db()
        self.assertIsNone(self.record.degree)
        self.assertIsNone(self.record.description)
