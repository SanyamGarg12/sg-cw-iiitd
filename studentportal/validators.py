from django.core.exceptions import ValidationError

def validate_credits(value):
	if value != 1 and value != 2:
		raise ValidationError('You can only work for 1 or 2 credits.')

def validate_feedback_hours(value):
	try:
		value = int(value)
	except:
		raise ValidationError('You must only enter integral number of hours.')
	if value < 0:
		raise ValidationError("Did you seriously work so litte ? Thanks for being honest.")
	elif value > 500:
		raise ValidationError("I don't believe you must have put in more than 500 hours, tops.")