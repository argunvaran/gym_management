from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def get_status(enrollments, lesson_id):
    enrollment = enrollments.filter(lesson_id=lesson_id).first()
    return enrollment.status if enrollment else 'Not Enrolled'

@register.filter
def custom_range(value):
    return range(1, value + 1)