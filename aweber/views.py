# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.base import RedirectView
from django.contrib.auth import login
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.http import Http404
from django.http import HttpResponseNotAllowed
import logging

from forms import AweberSignupFullNameEmailConfirmedPasswordSegmentForm
from utils import get_aweber_params
from utils import create_new_user
from utils import is_email_valid
from utils import encode_email
from utils import get_user_by_email_or_none
import signals
import defaults

logger = logging.getLogger(__name__)

class AweberSubscriptionFormProcessView(
    FormView
    ):

    """ This is where the aweber subscription happens """
    template_name = "aweber/aweber_subscription_form_process_view.html"
    form_class = AweberSignupFullNameEmailConfirmedPasswordSegmentForm
    success_url = reverse_lazy('aweber_subscription_form_auto_submit')
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(AweberSubscriptionFormProcessView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

    def post(self, request, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            self.request.session['aweber_subscription_form_data'] = form.clean()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class AweberSubscriptionFormAutoSubmitView(
    TemplateView
    ):
    """ 
    The user subscription is requested and confirmation is sent for double opt-in.
    Aweber needs to get all sort of information from the user. So we auto submit a 
    form on behalf of the user to Aweber using JS while validating the form locally.
    """
    template_name = "aweber/aweber_subscription_form_auto_submit_view.html"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(AweberSubscriptionFormAutoSubmitView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        try:
            form_data = self.request.session['aweber_subscription_form_data']
        except:
            logger.error('Cannot locate aweber post data in session')
            raise Http404
    
        context['list_name'] = defaults.AWEBER_LIST_NAME
        context['subscribed_callback'] = defaults.AWEBER_SUBSCRIBED_CALLBACK_URL
        context['already_subscribed_callback'] = defaults.AWEBER_ALREADY_SUBSCRIBED_CALLBACK_URL
        context['name'] = form_data.get('full_name', '')
        context['email'] = form_data.get('email', '')
        context['segment'] = form_data.get('segment', '')
        context['token'] = encode_email(context['email'])
        context['aweber_subscription_success'] = True
        return context


class AweberConfirmationSubscriptionCallbackView(
    TemplateView
    ):
    """ 
    The user subscription request sent, we were called back (aweber says: new user).
    This is when a new user creates a new account, aweber sends verification email, so
    we wait for Aweber to tell us when the double opt-in is complete, then we activate
    the account
    """
    template_name = "aweber/aweber_subscription_confirmation_callback_view.html"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(AweberConfirmationSubscriptionCallbackView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        try:
            form_data = self.request.session['aweber_subscription_form_data']
        except:
            logger.error('Cannot locate aweber post data in session')
            raise Http404

        context['name'] = form_data.get('name', '')
        context['email'] = form_data.get('email', '')
        context['segment'] = form_data.get('segment', '')
        new_user = create_new_user(context['email'], context['name'], form_data.get('password', ''))
        signals.user_subscribed.send(sender=signals.AweberSignalSender, user=new_user, request=self.request)
        
        del self.request.session['aweber_subscription_form_data']

        return context


class AweberConfirmationResubscriptionCallbackView(
    TemplateView
    ):
    """ 
    The user resubscription request sent, we were called back (aweber says: existing user)
    This is when a user first completes subscription, then deletes her/his account without
    unsubscribing from aweber, then later on decides to recreate and account.
    Since Aweber has already verified the email address, we just create the account and 
    let the user login.
    """
    template_name = "aweber/aweber_subscription_complete_view.html"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(AweberConfirmationResubscriptionCallbackView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        try:
            form_data = self.request.session['aweber_subscription_form_data']
        except:
            logger.error('Cannot locate aweber post data in session')
            raise Http404

        context['name'] = form_data.get('name', '')
        context['email'] = form_data.get('email', '')
        context['segment'] = form_data.get('segment', '')
        new_user = create_new_user(context['email'], context['name'], form_data.get('password', ''), is_active=True)
        signals.user_resubscribed.send(sender=signals.AweberSignalSender, user=new_user, request=self.request)
        
        return context


class AweberConfirmationSubscriptionLinkClickedView(
    RedirectView
    ):
    """
    The user confirmed the subscription, we capture the params and redirect right away.
    This is a redirecct view so the GET params are not visible to long. A token is also 
    used for extra security measures and verification.
    """
    
    def get_redirect_url(self, **kwargs):
        self.request.session['aweber_data'] = get_aweber_params(self.request.GET)
        if "meta_adtracking" in self.request.session['aweber_data']:
            self.request.session['aweber_data']['segment'] = self.request.session['aweber_data']['meta_adtracking']
        return reverse_lazy('aweber_subscription_complete')


class AweberSubscriptionCompleteView(
    TemplateView
    ):
    """ 
    The user confirmed the subscription. (Aweber says: double opt-in complete)
    If user has already clicked on verification link, then we just let the user login.
    If user just clicked on verification link, then we activate the account and let the user login
    """
    template_name = "aweber/aweber_subscription_complete_view.html"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(AweberSubscriptionCompleteView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        try:
            aweber_data = self.request.session['aweber_data']
        except:
            logger.error('Cannot locate aweber params in session')
            raise Http404

        context['email'] = aweber_data.get('email', '')
        context['token'] = aweber_data.get('custom token', '')
        context['name'] = aweber_data.get('name', '')
        context['first_name'] = aweber_data.get('first_name', '')
        context['last_name'] = aweber_data.get('last_name', '')
        context['segment'] = aweber_data.get('meta_adtracking', '')
        context['new_user'] = get_user_by_email_or_none(context['email'])
        
        return context

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        
        if not is_email_valid(context['email'], context['token']):
            logger.error('Invalid token. Cannot trust the request')
            raise Http404
    
        new_user = context['new_user']
        if not new_user:
            logger.error('Something went wrong. Cannot locate inactive user')
            raise Http404
        
        if new_user.is_active:
            return HttpResponseRedirect(reverse_lazy('auth_login'))

        new_user.is_active = True
        new_user.save()
        signals.user_verified.send(sender=signals.AweberSignalSender, user=new_user, request=self.request)
        
        return super(AweberSubscriptionCompleteView, self).get(self.request, *args, **kwargs)



