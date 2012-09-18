# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import defaults


class AweberSignupPasswordFormMixin(forms.Form):
    """ Ask user for password once """
    password1 = forms.CharField(
                label = _("Password"),
                widget = forms.PasswordInput,
                required = True,
                max_length = 75,
                help_text = _("Please choose a strong password")
    )

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1', '')
        min_len = getattr(defaults, "AWEBER_PASSWORD_MINIMUM_LENGHT", 6)
        if len(password1) < min_len:
            raise forms.ValidationError(_("Password too short! minimum length is ")+" [%d]" % min_len)

        return password1


class AweberSignupConfirmedPasswordFormMixin(AweberSignupPasswordFormMixin):
    """ Ask user for password twice """
    def __init__(self, *args, **kwargs):
        super(AweberSignupConfirmedPasswordFormMixin, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'password1',
            'password2',
        ]
        
    password2 = forms.CharField(
                label = _("Confirm Password"),
                widget = forms.PasswordInput,
                required = True,
                max_length = 75,
                help_text = _("To make sure you have entered your password correctly")
    )
        
    def clean_password2(self):
        """ Confirm passwords are the same and not too short """
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data.get('password2', '')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))

        return password2


class AweberSignupEmailFormMixin(forms.Form):
    """ Ask user for email once """
    email1 = forms.EmailField(
                label = _("Email"),
                max_length = 75,
                required = True,
                help_text = _("Please user a valid email address")
    )

    def clean_email1(self):
        """ Email should be unique """
        email1 = self.cleaned_data.get('email1', '').lower()
        verify = getattr(defaults, 'AWEBER_VERIFY_IF_EMAIL_EXISTS', False)
        if verify:
            try:
                from emailahoy import verify_email_address
            except:
                raise ImproperlyConfigured('AWEBER_VERIFY_IF_EMAIL_EXISTS is set but python-emailahoy is not installed')
            if not verify_email_address(email1):
                raise forms.ValidationError(_("Email address rejected. Please use a REAL and working email address."))
                
        if User.objects.filter(email__iexact=email1):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return email1


class AweberSignupConfirmedEmailFormMixin(AweberSignupEmailFormMixin):
    """ Ask user for email twice """
    def __init__(self, *args, **kwargs):
        super(AweberSignupConfirmedEmailFormMixin, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'email1',
            'email2',
        ]
    
    email2 = forms.EmailField(
                label = _("Confirm Email"),
                max_length = 75,
                required = True,
                help_text = _("To make sure you have entered your email address correctly")
    )

    def clean_email2(self):
        """ Confirm emails are the same """
        email1 = self.cleaned_data.get('email1', '').lower()
        email2 = self.cleaned_data.get('email2', '').lower()
        if email1 and email2:
            if email1 != email2:
                raise forms.ValidationError(_("The two email address fields didn't match."))
        return email2


class AweberSignupFullNameFormMixin(forms.Form):
    """ Ask the user for full name """

    full_name = forms.CharField(
                label = _("Full name"), 
                max_length=120, 
                required=True,
                help_text = _("Your first name + last name (surname) - e.g. John Smith.")
    )

    def clean_full_name(self):
        """ Ensure that the user gives first and last name """
        full_name = self.cleaned_data.get('full_name', '').title()
        names = full_name.split(' ')
        if len(names) == 1:
            raise forms.ValidationError(_("Please enter your full name"))
        elif len(names) == 2:
            if len(names[0]) < 2:
                raise forms.ValidationError(_("Please enter your first name"))
            elif len(names[1]) < 2:
                raise forms.ValidationError(_("Please enter your last name"))
        elif len(names) >= 3:
            if len(names[0]) < 2:
                raise forms.ValidationError(_("Please enter your first name"))
            elif len(names[2]) < 2:
                raise forms.ValidationError(_("Please enter your last name"))
        return full_name


class AweberFormWithSegmentMixin(forms.Form):

    try:
        AWEBER_LIST_SEGMENT = getattr(defaults, 'AWEBER_LIST_SEGMENT')
    except AttributeError:
        raise ImproperlyConfigured('AWEBER_LIST_SEGMENT is missing from your project settings')
            
    segment = forms.ChoiceField(
                label = _('List Segment'), 
                choices = AWEBER_LIST_SEGMENT,
                required = True,
                help_text = _("Please choose with care, as you cannot change this later!")
    )


class AweberSignupFullNameEmailForm(AweberSignupFullNameFormMixin, AweberSignupEmailFormMixin):
    """ Ask the user for email and full name """
    def __init__(self, *args, **kwargs):
        super(AweberSignupFullNameEmailForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'full_name',
            'email1',
        ]


class AweberSignupFullNameEmailPasswordForm(AweberSignupFullNameEmailForm, AweberSignupPasswordFormMixin):
    """ Ask the user for email and full name and password"""
    def __init__(self, *args, **kwargs):
        super(AweberSignupFullNameEmailPasswordForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'full_name',
            'email1',
            'password1',
        ]


class AweberSignupFullNameEmailPasswordSegmentForm(AweberSignupFullNameEmailPasswordForm, AweberFormWithSegmentMixin):
    """ Ask the user for email and full name """
    def clean(self):
        def __init__(self, *args, **kwargs):
            super(AweberSignupFullNameEmailPasswordForm, self).__init__(*args, **kwargs)
            self.fields.keyOrder = [
                'full_name',
                'email1',
                'password1',
                'segment',
            ]






