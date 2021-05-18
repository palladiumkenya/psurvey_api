from celery import task
from celery import shared_task
from datetime import date

from .models import Questionnaire


@shared_task
def quest_active_check():
    queryset = Questionnaire.objects.filter(active_till__lt=date.today(), is_active=True)
    for q in queryset:
        qu = Questionnaire.objects.get(id=q.id)
        qu.is_active = False
        qu.save()
    return 'i am here'
    # Another trick
