import uuid

from django.db import models
from django.template.defaultfilters import slugify


class UUIDMixin(object):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class NonUniqueSlugMixin(object):
    slug = models.CharField("Slug", max_length=50)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(NonUniqueSlugMixin, self).save(*args, **kwargs)
