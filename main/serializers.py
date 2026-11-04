from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Experience, Education
from main.validators import validate_date_range


class PortfolioSerializer(serializers.ModelSerializer):
    """Shared validation and read-only star data for portfolio entries."""

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    def validate(self, attrs):
        # PATCH may omit either date; validate against the saved value as well.
        started_at = attrs.get("started_at", getattr(self.instance, "started_at", None))
        ended_at = attrs.get("ended_at", getattr(self.instance, "ended_at", None))
        try:
            validate_date_range(started_at, ended_at)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error
        return attrs

    @staticmethod
    def clean_text(value):
        # Nullable fields must remain null, rather than becoming the text "None".
        return None if value is None else strip_tags(value)

    def validate_description(self, value):
        return self.clean_text(value)

    def starred_users(self, obj):
        """Read each entry's stars once, reusing prefetched users when available.

        All three computed fields consume the same list. Without prefetching,
        fetch only the user columns used by the API, once per entry.
        """
        cache = self.__dict__.setdefault("_starred_users_by_id", {})
        if obj.pk not in cache:
            prefetched = getattr(obj, "_prefetched_objects_cache", {})
            users = prefetched.get("starred_by")
            if users is None:
                users = obj.starred_by.only("id", "username")
            cache[obj.pk] = list(users)
        return cache[obj.pk]

    def get_star_count(self, obj):
        return len(self.starred_users(obj))

    def get_is_starred(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and any(
            user.pk == request.user.pk for user in self.starred_users(obj)
        ))

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in self.starred_users(obj))


class ExperienceSerializer(PortfolioSerializer):
    class Meta:
        model = Experience
        fields = [
            "id", "title", "description", "category",
            "thumbnail", "started_at", "ended_at",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_category(self, value):
        return self.clean_text(value)


class EducationSerializer(PortfolioSerializer):
    class Meta:
        model = Education
        fields = [
            "id", "institution_name", "degree",
            "description", "started_at", "ended_at",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_institution_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Institution name cannot be empty.")
        return value

    def validate_degree(self, value):
        return self.clean_text(value)
