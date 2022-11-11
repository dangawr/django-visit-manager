from django.urls import path
from .views import IndexView, SignInView, UpdateVisitView, CreateVisitView
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'booking'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('login/', LoginView.as_view(template_name='booking/login.html'), name='login'),
    path('visit-edit/<int:pk>/', UpdateVisitView.as_view(), name='visit-edit'),
    path('visit-create/', CreateVisitView.as_view(), name='visit-create')
]
