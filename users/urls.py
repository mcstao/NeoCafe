from django.urls import path
from .views import (
    CustomerLoginView,
    ConfirmCustomerLoginView,
    WaiterLoginView,
    ConfirmBaristaWaiterLoginView,
    AdminLoginView,
    VerifyEmailView,
    CustomerRegistrationView, ResendOtpView, BaristaLoginView
)

urlpatterns = [
    path('login/customer/', CustomerLoginView.as_view(), name='customer-login'),
    path('login/customer/confirm/', ConfirmCustomerLoginView.as_view(), name='confirm-customer-login'),
    path('login/waiter/', WaiterLoginView.as_view(), name='waiter-login'),
    path('login/waiter/confirm/', ConfirmBaristaWaiterLoginView.as_view(), name='confirm-barista-waiter-login'),
    path('login/admin/', AdminLoginView.as_view(), name='admin-login'),
    path('verify/email/', VerifyEmailView.as_view(), name='verify-email'),
    path('register/customer/', CustomerRegistrationView.as_view(), name='customer-registration'),
    path('login/barista/confirm/', ConfirmBaristaWaiterLoginView.as_view(),name='confirm-barista-waiter-login'),
    path("resend-code/", ResendOtpView.as_view(),  name='resend-otp'),
    path('login/barista/', BaristaLoginView.as_view(), name='barista-login')
]