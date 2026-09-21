from django.forms import ModelForm, TextInput, Textarea, URLInput, Select, DateInput
from main.models import Experience, Education

class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "started_at",
            "ended_at",
        ]

        labels = {
            "title": "Posisi / Nama Pengalaman",
            "description": "Deskripsi Pengalaman",
            "category": "Kategori Pengalaman",
            "thumbnail": "URL Thumbnail",
            "started_at": "Tanggal Mulai",
            "ended_at": "Tanggal Selesai",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Software Engineering Intern",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan peran, tanggung jawab, dan pencapaianmu...",
                    "rows": 4,
                }
            ),
            "category": Select(
                attrs={
                    # Widget Select otomatis menggunakan EXPERIENCE_CHOICES dari model
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
            "started_at": DateInput(
                attrs={
                    "type": "date",  # Memunculkan kalender di browser
                }
            ),
            "ended_at": DateInput(
                attrs={
                    "type": "date",  # Memunculkan kalender di browser
                }
            ),
        }

class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution_name",
            "degree",
            "description",
            "started_at",
            "ended_at",
        ]

        labels = {
            "institution_name": "Nama Institusi",
            "degree": "Gelar / Program Studi",
            "description": "Deskripsi",
            "started_at": "Tanggal Mulai",
            "ended_at": "Tanggal Selesai",
        }

        widgets = {
            "institution_name": TextInput(
                attrs={
                    "placeholder": "Contoh: Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "degree": TextInput(
                attrs={
                    "placeholder": "Contoh: Sarjana Ilmu Komputer",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pengalaman, pencapaian, atau aktivitas selama masa pendidikan",
                    "rows": 3,
                }
            ),
            "started_at": DateInput(
                attrs={
                    "type": "date", # Menggunakan HTML5 date picker
                }
            ),
            "ended_at": DateInput(
                attrs={
                    "type": "date", # Menggunakan HTML5 date picker
                }
            ),
        }