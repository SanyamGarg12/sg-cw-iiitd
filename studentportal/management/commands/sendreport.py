from django.core.management.base import NoArgsCommand, make_option

class Command(NoArgsCommand):
    help = "Checks and sends daily reports to the admins"

    def handle_noargs(self, **options):
        from studentportal import adapters
        adapters.send_report_to_admins()