from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Coupon(models.Model):
    code = models.CharField(max_length=64, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(
        validators=(
            MinValueValidator(0),
            MaxValueValidator(100),
        ),
        help_text='percent value (0 to 100)'
    )
    active = models.BooleanField()

    class Meta:
        ordering = ('code',)
        indexes = (
            models.Index(fields=('code',)),
        )

    def __str__(self) -> str:
        return self.code
