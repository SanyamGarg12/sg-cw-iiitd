class notification_type(object):
	NEW_PROJECT, PROJECT_EDITED, PROJECT_FINISHED, NGO_SUGGESTION = range(1,5)

nt = notification_type()

def add_notification(noti_type, **kwargs):
	# this is very very very problematic
	from supervisor.models import Notification
	if noti_type in [nt.NEW_PROJECT, nt.PROJECT_EDITED]:
		Notification.objects.create(noti_type=noti_type,
									project=kwargs['project'])
	elif noti_type == nt.NGO_SUGGESTION:
		Notification.objects.create(noti_type=noti_type,
                NGO_name=kwargs['name'],
                NGO_link=kwargs['link'],
                NGO_details=kwargs['details'],
                NGO_sugg_by=kwargs['NGO_sugg_by'])