"""
Unfortunately this is a Django limitation as there must be a models module in the app root
directory. We want our SQL implementation to live in notifications.store.sql so
lets import everything from there
"""

from notifications.store.mysql.models import *
