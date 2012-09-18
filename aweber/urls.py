from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',

    url(r'^$',
        AweberSubscriptionFormProcessView.as_view(),
        name='aweber_subscription_form_process'
    ),

    url(r'^subscription/submit/$',
        AweberSubscriptionFormAutoSubmitView.as_view(),
        name='aweber_subscription_form_auto_submit'
    ),
    
    url(r'^subscription/thanks/$',
        AweberConfirmationSubscriptionCallbackView.as_view(),
        name='aweber_subscription_confirmation_callback'
    ),

    url(r'^resubscription/thanks/$',
        AweberConfirmationResubscriptionCallbackView.as_view(),
        name='aweber_resubscription_reconfirmation_callback'
    ),
    
    url(r'^subscription/confirmed/$',
        AweberConfirmationSubscriptionLinkClickedView.as_view(),
        name='aweber_subscription_confirmation_link_clicked'
    ),

    url(r'^subscription/complete/$',
        AweberSubscriptionCompleteView.as_view(),
        name='aweber_subscription_complete'
    ),
)