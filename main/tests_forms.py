from datetime import date

from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.utils import translation

from main.forms import EducationForm, ExperienceForm
from main.models import Education, Experience


class UpdateDateInputTest(SimpleTestCase):
    def test_existing_dates_use_html_date_format_in_each_language(self):
        for form_class, instance in (
            (EducationForm, Education(started_at=date(2025, 7, 1), ended_at=date(2029, 8, 1))),
            (ExperienceForm, Experience(started_at=date(2025, 7, 1), ended_at=date(2029, 8, 1))),
        ):
            for language in ("en-us", "id"):
                with self.subTest(form=form_class.__name__, language=language), translation.override(language):
                    form = form_class(instance=instance)
                    self.assertIn('value="2025-07-01"', str(form["started_at"]))
                    self.assertIn('value="2029-08-01"', str(form["ended_at"]))

    def test_ongoing_experience_end_date_remains_blank(self):
        form = ExperienceForm(instance=Experience(started_at=date(2025, 7, 1)))
        self.assertNotIn('value=', str(form["ended_at"]))

    def test_models_reject_end_dates_before_start_dates(self):
        for model in (Experience, Education):
            with self.subTest(model=model.__name__):
                entry = model(started_at=date(2026, 2, 1), ended_at=date(2026, 1, 1))
                with self.assertRaises(ValidationError) as error:
                    entry.clean()
                self.assertIn("ended_at", error.exception.message_dict)

    def test_experience_form_rejects_invalid_dates_and_accepts_ongoing_entries(self):
        payload = {
            "title": "Research", "description": "Description", "category": "research",
            "started_at": "2026-02-01", "ended_at": "2026-01-01",
        }
        form = ExperienceForm(data=payload)
        self.assertFalse(form.is_valid())
        self.assertIn("ended_at", form.errors)
        form = ExperienceForm(data={**payload, "ended_at": ""})
        self.assertTrue(form.is_valid(), form.errors)
