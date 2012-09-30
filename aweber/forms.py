# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import defaults


class AweberSignupPasswordFormMixin(forms.Form):
    """ Ask user for password once """
    password = forms.CharField(
                label = _("Password"),
                widget = forms.PasswordInput,
                required = True,
                max_length = 75,
                help_text = _("Please choose a strong password. (minimum of %d characters)" % defaults.AWEBER_PASSWORD_MINIMUM_LENGHT)
    )

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if len(password) < defaults.AWEBER_PASSWORD_MINIMUM_LENGHT:
            raise forms.ValidationError(_("Password too short! minimum length is ")+" [%d]" % defaults.AWEBER_PASSWORD_MINIMUM_LENGHT)

        return password


class AweberSignupConfirmedPasswordFormMixin(AweberSignupPasswordFormMixin):
    """ Ask user for password twice """
    def __init__(self, *args, **kwargs):
        super(AweberSignupConfirmedPasswordFormMixin, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'password',
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
        password = self.cleaned_data.get('password', '')
        password2 = self.cleaned_data.get('password2', '')
        if password and password2:
            if password != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))

        return password2


class AweberSignupEmailFormMixin(forms.Form):
    """ Ask user for email once """
    email = forms.EmailField(
                label = _("Email"),
                max_length = 75,
                required = True,
                help_text = _("Please use a valid email address and avoid typos")
    )

    def clean_email(self):
        """ Email should be unique """
        email = self.cleaned_data.get('email', '').lower()
        
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        
        if defaults.AWEBER_VERIFY_IF_EMAIL_EXISTS:
            try:
                from emailahoy import verify_email_address
            except:
                raise ImproperlyConfigured('AWEBER_VERIFY_IF_EMAIL_EXISTS is set but python-emailahoy is not installed')
            if not verify_email_address(email):
                raise forms.ValidationError(_("Email address rejected. Please use a REAL and working email address."))
        
        return email


class AweberSignupConfirmedEmailFormMixin(AweberSignupEmailFormMixin):
    """ Ask user for email twice """
    def __init__(self, *args, **kwargs):
        super(AweberSignupConfirmedEmailFormMixin, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'email',
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
        email = self.cleaned_data.get('email', '').lower()
        email2 = self.cleaned_data.get('email2', '').lower()
        if email and email2:
            if email != email2:
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

    if defaults.AWEBER_LIST_SEGMENT == []:
        raise ImproperlyConfigured('AWEBER_LIST_SEGMENT is missing from your project settings')
    
    defaults.AWEBER_LIST_SEGMENT.insert(0, ('', '------------'))
    segment = forms.ChoiceField(
                label = _('Subscription Type'), 
                choices = defaults.AWEBER_LIST_SEGMENT,
                required = True,
                help_text = _("Please choose with care, as you cannot change this later!")
    )

    def clean_segment(self):
        segment = self.cleaned_data.get('segment', [])
        return segment
        

class AweberSignupFullNameEmailForm(AweberSignupFullNameFormMixin, AweberSignupEmailFormMixin):
    """ Ask the user for email and full name """
    def __init__(self, *args, **kwargs):
        super(AweberSignupFullNameEmailForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'full_name',
            'email',
        ]


class AweberSignupFullNameEmailPasswordForm(AweberSignupFullNameEmailForm, AweberSignupPasswordFormMixin):
    """ Ask the user for email and full name and password"""
    def __init__(self, *args, **kwargs):
        super(AweberSignupFullNameEmailPasswordForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'full_name',
            'email',
            'password',
        ]


class AweberSignupFullNameEmailConfirmedPasswordForm(AweberSignupFullNameEmailForm, AweberSignupConfirmedPasswordFormMixin):
    """ Ask the user for email and full name and password"""
    def __init__(self, *args, **kwargs):
        super(AweberSignupFullNameEmailConfirmedPasswordForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'full_name',
            'email',
            'password',
            'password2',
        ]
                
class AweberSignupFullNameEmailPasswordSegmentForm(AweberSignupFullNameEmailPasswordForm, AweberFormWithSegmentMixin):
    """ Ask the user for email and full name, password and segment """
    def __init__(self, *args, **kwargs):
        super(AweberSignupFullNameEmailPasswordSegmentForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'full_name',
            'email',
            'password',
            'segment',
        ]

class AweberSignupFullNameEmailConfirmedPasswordSegmentForm(AweberSignupFullNameEmailConfirmedPasswordForm, AweberFormWithSegmentMixin):
    """ Ask the user for email and full name, password(s) and segment """
    def __init__(self, *args, **kwargs):
        super(AweberSignupFullNameEmailConfirmedPasswordSegmentForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'full_name',
            'email',
            'password',
            'password2',
            'segment',
        ]



