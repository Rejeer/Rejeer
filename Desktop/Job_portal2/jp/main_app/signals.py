from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Application, Notification

@receiver(post_save, sender=Application)
def notify_company(sender, instance, created, **kwargs):
    if created:
        # Create a notification for the company when a new application is submitted
        Notification.objects.create(
            job=instance.job,
            message=f'New application received for {instance.job.title} by {instance.seeker.username}',
            company=instance.job.company  # Assuming `job.company` is the company field
        )
