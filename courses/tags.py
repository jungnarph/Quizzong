from taggit.models import TagBase, GenericTaggedItemBase
from django.utils.text import slugify
from django.db import models

class SluggedTag(TagBase):
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.name = self.slug  # Ensure name is stored in slug format too
        super().save(*args, **kwargs)


class TaggedQuestion(GenericTaggedItemBase):
    tag = models.ForeignKey(
        SluggedTag,
        related_name="tagged_questions",
        on_delete=models.CASCADE,
    )