# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.http import Http404
from forms import AweberSignupFullNameEmailConfirmedPasswordSegmentForm
from utils import get_aweber_args
from utils import get_user_or_none
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
        
        if not defaults.AWEBER_LIST_NAME:
            raise ImproperlyConfigured('AWEBER_LIST_NAME is missing from your project settings')
            
        context['list_name'] = defaults.AWEBER_LIST_NAME
        context['thank_you'] = defaults.AWEBER_THANK_YOU_PAGE
        context['already_subscribed'] = defaults.AWEBER_ALREADY_SUBSCRIBED_PAGE
        context['full_name'] = form_data.get('full_name', '')
        context['email'] = form_data.get('email1', '')
        context['segment'] = form_data.get('segment', '')
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
        
        context['full_name'] = form_data.get('full_name', '')
        context['email'] = form_data.get('email', '')
        context['segment'] = form_data.get('segment', '')
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
    
        context['full_name'] = form_data.get('full_name', '')
        context['email'] = form_data.get('email', '')
        context['segment'] = form_data.get('segment', '')
        del self.request.session['aweber_subscription_form_data']

        return context


class AweberConfirmationSubscriptionLinkClickedView(
    TemplateView
    ):
    """ The user confirmed the subscription """
    template_name = "aweber/aweber_subscription_complete_view.html" # not used
    success_url = reverse_lazy('aweber_subscription_complete')

    def get(self, *args, **kwargs):
        args = get_aweber_args(self.request)
        self.request.session['full_name'] = args.get('full_name', '')
        self.request.session['email'] = args.get('email', '')
        return HttpResponseRedirect(self.success_url)


class AweberSubscriptionCompleteView(
    TemplateView
    ):
    """ The user confirmed the subscription """
    template_name = "aweber/aweber_subscription_complete_view.html"

    def get(self, *args, **kwargs):
        user = get_user_or_none(self.request.session['email'])
        if user:
            user.is_active = True
            user.save()
        else:    
            raise Http404
                    
        return super(AweberSignupSubscriptionCompleteView, self).get(*args, **kwargs)






