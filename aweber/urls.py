from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',

    url(r'^$',
        AweberSubscriptionFormProcessView.as_view(),
        name='aweber_subscription_form_process'
    ),

    url(r'^submit/$',
        AweberSubscriptionFormAutoSubmitView.as_view(),
        name='aweber_subscription_form_auto_submit'
    ),
    
    url(r'^thanks/$',
        AweberConfirmationSubscriptionCallbackView.as_view(),
        name='aweber_subscription_confirmation_callback'
    ),

    url(r'^thanks-again/$',
        AweberConfirmationResubscriptionCallbackView.as_view(),
        name='aweber_resubscription_reconfirmation_callback'
    ),
    
    url(r'^confirmed/$',
        AweberConfirmationSubscriptionLinkClickedView.as_view(),
        name='aweber_subscription_confirmation_link_clicked'
    ),

    url(r'^complete/$',
        AweberSubscriptionCompleteView.as_view(),
        name='aweber_subscription_complete'
    ),
)