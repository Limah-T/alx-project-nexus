from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from django.urls import path

from .auth_views import CustomerRegView, VendorRegView, LoginView, ResetPasswordView, SetPasswordView, ChangePasswordView, LogoutView, verifyRegEmail, verifyPasswordResetEmail, verifyEmailUpdate, verifyAcctDeactivation, CustomerProfileView, VendorProfileView

from .views import CategoryView, ColorView, ProductView

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

    # token refresh view
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # email verification
    path('verify_email/register', verifyRegEmail, name="verify_reg_email"),
    path('verify/password_reset', verifyPasswordResetEmail, name="verify_password_reset"),
    path('verify/email_update', verifyEmailUpdate, name='verify_email_update'),
    path('verify/acct_deactivation', verifyAcctDeactivation, name='verify_acct_deactivate'),
    
    # profile 
    path('customer/profile/', CustomerProfileView.as_view({'get': 'retrieve', 'put': 'update',  
                                                           'patch': 'update', 'delete': 'destroy'}), name='customer_profile'),
    path('vendor/profile/', VendorProfileView.as_view({'get': 'retrieve', 'put': 'update', 
                                                       'patch': 'update', 'delete': 'destroy'}), name='vendor_profile'),
    
    # admin routes
    path('users/', ModifyUserView.as_view({'get': 'list'}), name='users'),
    path('user/<uuid:id>/', ModifyUserView.as_view({'get': 'retrieve', 'delete': 'destroy'}),
                                                    name='user'),

    # Category
    path('category/', CategoryView.as_view({'post': 'create', 'get': 'list'}), name='category'),
    path('category/<uuid:id>', CategoryView.as_view({'get': 'retrieve', 
                                                     'put': 'update', 'patch':'update', 'delete': 'destroy'}), name='category_id'
                                            ),
    # Color
    path('color/', ColorView.as_view({'post': 'create', 'get': 'list'}), name='color'),
    path('color/<uuid:id>', ColorView.as_view({'get': 'retrieve', 
                                                     'put': 'update', 'patch':'update', 'delete': 'destroy'}), name='color_id'
                                            ),

    # Product
    path('product/', ProductView.as_view({'post': 'create', 'get': 'list'}), name='product'),
    path('product/<uuid:id>', ProductView.as_view({'get': 'retrieve', 'put': 'update',
                                                   'patch': 'update', 'delete': 'destroy'}), name='product_id'
                                            ),
]
