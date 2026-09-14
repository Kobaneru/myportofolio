import uuid
from django.db import models
from django.core.exceptions import ValidationError

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
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Education(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution_name = models.CharField(max_length=255)
    degree = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    started_at = models.DateField()
    ended_at = models.DateField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ended_at__gte=models.F('started_at')),
                name='education_ended_at_gte_started_at',
            )
        ]
        ordering = ['-started_at']

    def clean(self):
        super().clean()
        if self.started_at and self.ended_at:
            if self.ended_at < self.started_at:
                raise ValidationError({
                    'ended_at': 'Tanggal berakhir tidak boleh lebih awal dari tanggal mulai.'
                })

    def __str__(self):
        if self.degree:
            return f"{self.degree} - {self.institution_name}"
        return self.institution_name