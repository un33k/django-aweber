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
from forms import AweberSignupFullNameEmailConfirmedPasswordSegmentForm
from utils import get_aweber_params
from utils import create_inactive_user
from utils import is_email_valid
from utils import encode_email
from utils import get_user_by_email_or_none

import defaults

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
    """ The user is subscribed and activation is sent """
    template_name = "aweber/aweber_subscription_form_auto_submit_view.html"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(AweberSubscriptionFormAutoSubmitView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        try:
            form_data = self.request.session['aweber_subscription_form_data']
        except:
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
    """ The user subscription request sent, we were called back """
    template_name = "aweber/aweber_subscription_confirmation_callback_view.html"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(AweberConfirmationSubscriptionCallbackView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        try:
            form_data = self.request.session['aweber_subscription_form_data']
        except:
            raise Http404

        context['name'] = form_data.get('name', '')
        context['email'] = form_data.get('email', '')
        context['segment'] = form_data.get('segment', '')
        create_inactive_user(context['email'], context['name'])
        del self.request.session['aweber_subscription_form_data']

        return context


class AweberConfirmationResubscriptionCallbackView(
    TemplateView
    ):
    """ The user resubscription request sent, we were called back """
    template_name = "aweber/aweber_subscription_confirmation_callback_view.html"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(AweberConfirmationResubscriptionCallbackView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        try:
            form_data = self.request.session['aweber_subscription_form_data']
        except:
            raise Http404

        context['name'] = form_data.get('name', '')
        context['email'] = form_data.get('email', '')
        context['segment'] = form_data.get('segment', '')
        create_inactive_user(context['email'], context['name'])
        return context


class AweberConfirmationSubscriptionLinkClickedView(
    RedirectView
    ):
    """ The user confirmed the subscription, capture the params and redirect right away """
    
    def get_redirect_url(self, **kwargs):
        self.request.session['aweber_data'] = get_aweber_params(self.request.GET)
        return reverse_lazy('aweber_subscription_complete')


class AweberSubscriptionCompleteView(
    TemplateView
    ):
    """ The user confirmed the subscription """
    template_name = "aweber/aweber_subscription_complete_view.html"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(AweberSubscriptionCompleteView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        try:
            aweber_data = self.request.session['aweber_data']
        except:
            raise Http404

        context['email'] = aweber_data.get('email', '')
        context['token'] = aweber_data.get('custom token', '')
        context['name'] = aweber_data.get('name', '')
        context['first_name'] = aweber_data.get('first_name', '')
        context['last_name'] = aweber_data.get('last_name', '')
        context['segment'] = aweber_data.get('meta_adtracking', '')
        context['inactive_user'] = get_user_by_email_or_none(context['email'])
        
        return context

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        
        if not is_email_valid(context['email'], context['token']):
            raise Http404
    
        inactive_user = context['inactive_user']
        if not inactive_user:
            raise Http404
        
        inactive_user.is_active = True
        inactive_user.save()

        return super(AweberSubscriptionCompleteView, self).get(self.request, *args, **kwargs)



