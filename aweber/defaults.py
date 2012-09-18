
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

AWEBER_SINGLE_OPT_IN = getattr(settings, 'AWEBER_SINGLE_OPT_IN', False)
AWEBER_VERIFICATION_EXPIRY = getattr(settings, 'AWEBER_VERIFICATION_EXPIRY', 5)
AWEBER_PASSWORD_MINIMUM_LENGHT = getattr(settings, 'AWEBER_PASSWORD_MINIMUM_LENGHT', 6)
AWEBER_VERIFY_IF_EMAIL_EXISTS = getattr(settings, 'AWEBER_VERIFY_IF_EMAIL_EXISTS', False)

AWEBER_LIST_SEGMENT = getattr(settings, 'AWEBER_LIST_SEGMENT', [])


