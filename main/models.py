import uuid
from django.db import models

class Achievement(models.Model):
    title = models.CharField(max_length=200)
    institution = models.CharField(max_length=100)
    description = models.TextField()
    year = models.CharField(max_length=4)
    badge_text = models.CharField(max_length=30)
    badge_variant = models.CharField(
        max_length=20, 
        default="badge-bronze",
        help_text="Nama class CSS, misal: badge-bronze atau badge-silver"
    )

    def __str__(self):
        return f"{self.title} ({self.year})"

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None