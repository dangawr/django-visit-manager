from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'booking'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signin/', views.SignInView.as_view(), name='signin'),
    path('login/', LoginView.as_view(template_name='booking/login.html'), name='login'),
    path('visit-edit/<int:pk>/', views.UpdateVisitView.as_view(), name='visit-edit'),
    path('visit-create/', views.CreateVisitView.as_view(), name='visit-create'),
    path('client-create/', views.CreateClientView.as_view(), name='client-create'),
    path('clients/', views.ClientsView.as_view(), name='clients'),
    path('client-edit/<int:pk>/', views.UpdateClientView.as_view(), name='client-edit'),
    path('client-delete/<int:pk>/',
         views.DeleteClientView.as_view(),
         name='client-delete'),
    path('visit-delete/<int:pk>/',
         views.DeleteVisitView.as_view(),
         name='visit-delete'),
    path('cancel-visits/', views.CancelVisitsView.as_view(), name='cancel-visits'),
    path('account/', views.UserAccountView.as_view(), name='account'),
]
