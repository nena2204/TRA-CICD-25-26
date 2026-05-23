from django.db import models
from django.utils import timezone
import uuid

class BuyOrder(models.Model):
    """
    Независен, безопасен модел (не го допира твојот постоечки модел).
    Користи се ако сакаш да ја користиш новата /buy/ рута.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_title = models.CharField(max_length=200)     # само текст, да не зависиме од твоите модели
    email = models.EmailField()
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name} – {self.event_title}"
