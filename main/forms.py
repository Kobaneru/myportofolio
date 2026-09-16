from django.forms import ModelForm, TextInput, Textarea, URLInput, Select, DateInput
from main.models import Experience

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