import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the first administrator from temporary environment variables, if needed."

    def handle(self, *args, **options):
        username = os.environ.get("INITIAL_ADMIN_USERNAME", "").strip()
        password = os.environ.get("INITIAL_ADMIN_PASSWORD", "")
        if not username or not password:
            self.stdout.write("No bootstrap credentials supplied; skipping administrator creation.")
            return
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write("Administrator account already exists; leaving it unchanged.")
            return
        User.objects.create_superuser(username=username, email="", password=password)
        self.stdout.write(self.style.SUCCESS("Initial administrator created."))
