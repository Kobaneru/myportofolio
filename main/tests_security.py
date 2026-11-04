from datetime import date

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Experience


class LegacyExperienceCSRFTest(TestCase):
    """Legacy routes must enforce CSRF even though the main page now uses DRF."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(username="owner", password="test-password")
        cls.experience = Experience.objects.create(
            title="Original", description="Description", category="research",
            started_at=date(2026, 1, 1),
        )

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.login(username="owner", password="test-password")
        self.payload = {
            "title": "Updated", "description": "Description", "category": "research",
            "started_at": "2026-01-01", "ended_at": "",
        }
        self.urls = {
            "create": reverse("main:create_experience_ajax"),
            "update": reverse("main:update_experience_ajax", args=[self.experience.id]),
            "delete": reverse("main:delete_experience_ajax", args=[self.experience.id]),
        }

    def assert_original_unchanged(self):
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Original")
        self.assertIsNone(self.experience.ended_at)

    def test_all_legacy_writes_without_token_are_rejected(self):
        for action, url in self.urls.items():
            with self.subTest(action=action):
                self.assertEqual(self.client.post(url, self.payload).status_code, 403)
                self.assert_original_unchanged()

    def test_all_legacy_writes_with_incorrect_token_are_rejected(self):
        self.client.get(reverse("main:show_experience"))
        for action, url in self.urls.items():
            with self.subTest(action=action):
                response = self.client.post(url, self.payload, HTTP_X_CSRFTOKEN="a" * 32)
                self.assertEqual(response.status_code, 403)
                self.assert_original_unchanged()

    def test_valid_token_allows_owner_create_update_and_delete(self):
        self.client.get(reverse("main:show_experience"))
        headers = {"HTTP_X_CSRFTOKEN": self.client.cookies["csrftoken"].value}
        self.assertEqual(self.client.post(self.urls["create"], self.payload, **headers).status_code, 201)
        self.assertEqual(Experience.objects.count(), 2)
        self.assertEqual(self.client.post(self.urls["update"], self.payload, **headers).status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Updated")
        self.assertEqual(self.client.post(self.urls["delete"], **headers).status_code, 200)
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_invalid_dates_do_not_write_through_legacy_routes(self):
        self.client.get(reverse("main:show_experience"))
        headers = {"HTTP_X_CSRFTOKEN": self.client.cookies["csrftoken"].value}
        for action in ("create", "update"):
            with self.subTest(action=action):
                response = self.client.post(self.urls[action], {
                    **self.payload, "ended_at": "2025-12-31",
                }, **headers)
                self.assertEqual(response.status_code, 400)
                self.assertIn("ended_at", response.json()["errors"])
                self.assert_original_unchanged()
