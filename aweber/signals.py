from django.dispatch import Signal

# A new user has subscribed. (Aweber says: New User)
user_subscribed = Signal(providing_args=["user", "request"])

# A user has resubscribed. (Aweber says: Existing User)
user_resubscribed = Signal(providing_args=["user", "request"])

# A user subscription is verified. (Aweber says: double opt-in complete)
user_verified = Signal(providing_args=["user", "request"])

class AweberSignalSender(object):
    pass


# from django.dispatch import receiver
# 
# @receiver(user_subscribed)
# def user_subscribed_callback(sender, **kwargs):
#     print "User %s subscribed ******" % kwargs['user'].username
# 
# 
# @receiver(user_resubscribed)
# def user_resubscribed_callback(sender, **kwargs):
#     print "User %s resubscribed ******" % kwargs['user'].username
# 
# 
# @receiver(user_verified)
# def user_verified_callback(sender, **kwargs):
#     print "User %s verified ******" % kwargs['user'].username
#     print kwargs['request'].session['aweber_data']
# 
# 
