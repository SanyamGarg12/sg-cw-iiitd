from django.apps import AppConfig

# import credentials
# from studentportal import startup
# import credentials
# from studentportal import startup


class SupervisorConfig(AppConfig):
    name = 'supervisor'

    # def ready(self):
    #     startup.work()
    #     credentials.init_firebase_keys()