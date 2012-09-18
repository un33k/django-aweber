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
from forms import AweberSignupFullNameEmailPasswordSegmentForm
from utils import get_aweber_args
from utils import get_user_or_none

class AweberSubscriptionFormProcessView(
    FormView
    ):
    
    """ This is where the aweber subscription happens """
    template_name = "aweber/aweber_subscription_form_process_view.html"
    form_class = AweberSignupFullNameEmailPasswordSegmentForm
    success_url = reverse_lazy('aweber_subscription_form_auto_submit')

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

    def get_context_data(self, **kwargs):
        ctx = super(AweberSubscriptionFormAutoSubmitView, self).get_context_data(**kwargs)
        try:
            form_data = self.request.session['aweber_subscription_form_data']
        except:
            form_data = {}
        
        if form_data:
            ctx['full_name'] = form_data.get('full_name', '')
            ctx['email'] = form_data.get('email1', '')
            ctx['segment'] = form_data.get('segment', '')
            ctx['aweber_subscription_success'] = True
        else:
            raise Http404
        return ctx


class AweberConfirmationSubscriptionCallbackView(
    TemplateView
    ):
    """ The user subscription request sent, we were called back """
    template_name = "aweber/aweber_subscription_confirmation_callback_view.html"

    def get_context_data(self, **kwargs):
        ctx = super(AweberConfirmationSubscriptionCallbackView, self).get_context_data(**kwargs)
        try:
            form_data = self.request.session['aweber_subscription_form_data']
        except:
            form_data = {}
        
        if form_data:            
            ctx['full_name'] = form_data.get('full_name', '')
            ctx['email'] = form_data.get('email', '')
            ctx['segment'] = form_data.get('segment', '')
            del self.request.session['aweber_subscription_form_data']
        else:
            raise Http404
        return ctx


class AweberConfirmationResubscriptionCallbackView(
    TemplateView
    ):
    """ The user resubscription request sent, we were called back """
    template_name = "aweber/aweber_subscription_reconfirmation_callback_view.html"

    def get_context_data(self, **kwargs):
        ctx = super(AweberConfirmationResubscriptionCallbackView, self).get_context_data(**kwargs)
        try:
            form_data = self.request.session['aweber_subscription_form_data']
        except:
            form_data = {}

        if form_data:
            ctx['full_name'] = form_data.get('full_name', '')
            ctx['email'] = form_data.get('email', '')
            ctx['segment'] = form_data.get('segment', '')
            self.request.session['aweber_subscription_form_data'] = None
        else:
            raise Http404
        return ctx


class AweberConfirmationSubscriptionLinkClickedView(
    TemplateView
    ):
    """ The user confirmed the subscription """
    template_name = "aweber_subscription/aweber_subscription_complete_view.html" # not used
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






