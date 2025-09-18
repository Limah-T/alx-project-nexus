from django.urls import path
from .auth_views import CustomerRegView, VendorRegView, LoginView, ResetPasswordView, SetPasswordView, ChangePasswordView, LogoutView, DeactivateAccountView, VerifyRegEmail, VerifyPasswordResetEmail
from .admin_views import ModifyUserView

urlpatterns = [
    # authentication routes
    path('customer/register/', CustomerRegView.as_view(), name='customer_register'),
    path('vendor/register/', VendorRegView.as_view(), name='vendor_register'),
    path('login/', LoginView.as_view(), name='login'),
    path('password/reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password/set/', SetPasswordView.as_view(), name='password_set'),
    path('password/change/', ChangePasswordView.as_view(), name='password_change'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('deactivate/account/', DeactivateAccountView.as_view(), name='deactivate_account'),

    # email verification
    path('verify_email/register', VerifyRegEmail, name="verify_reg_email"),
    path('verify/password_reset', VerifyPasswordResetEmail, name="verify_password_reset"),

    # admin routes
    path('users/', ModifyUserView.as_view({'get': 'list'}), name='users'),
    path('user/<uuid:id>/', ModifyUserView.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='user'),

]