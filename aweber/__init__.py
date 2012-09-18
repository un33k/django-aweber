# -*- coding: utf-8 -*-
import os
import pkg_resources

try:
    _s = os.environ['DJANGO_SETTINGS_MODULE']
except KeyError:
    # DJANGO_SETTINGS_MODULE should have been set by now, if not, we must be in test mode
    os.environ['DJANGO_SETTINGS_MODULE'] = 'aweber.testsettings'
