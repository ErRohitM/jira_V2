from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from common.middleware import get_current_user


class BaseModels(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Fields to track the user who created or last updated the object
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,  # Make it non-mandatory
        blank=True,  # Allow blank fields
        related_name='%(class)s_created',
        verbose_name='Created by'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,  # Make it non-mandatory
        blank=True,  # Allow blank fields
        related_name='%(class)s_updated',
        verbose_name='Updated by'
    )

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not self.pk:  # New object
            self.created_by = user
        if user:  # Existing or new object
            self.updated_by = user
        super().save(*args, **kwargs)