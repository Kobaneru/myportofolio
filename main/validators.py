from django.core.exceptions import ValidationError


def validate_date_range(started_at, ended_at):
    """Allow an ongoing entry; otherwise require its end to follow its start.

    Models and DRF serializers share this rule so HTML forms, admin, and JSON
    requests reject the same invalid date range. Equal dates remain valid.
    """
    if started_at and ended_at and ended_at < started_at:
        raise ValidationError({
            "ended_at": "Tanggal berakhir tidak boleh lebih awal dari tanggal mulai.",
        })
