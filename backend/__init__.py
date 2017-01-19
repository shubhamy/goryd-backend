from __future__ import absolute_import
from .celery import app as celery_app
# import datetime
# from django.utils.timezone import is_aware
# import djcelery.snapshot
#
# orig_maybe_make_aware = djcelery.snapshot.maybe_make_aware
# def new_maybe_make_aware(value):
#     if isinstance(value, datetime.datetime) and is_aware(value):
#         return value
#     return orig_maybe_make_aware(value)
# djcelery.snapshot.maybe_make_aware = new_maybe_make_aware
