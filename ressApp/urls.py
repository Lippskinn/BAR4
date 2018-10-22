from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import password_change
from . import views

'''
urls: Pfadgerüst der Templates mit der zugehörigen Logik (view)
authors: David Hartmann, Simon Hoffmann, Julian Sears
'''

urlpatterns = [
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),
    path('account/save/', views.signup, name='account'),
    path('<int:offer_id>/', views.detail, name='detail'),
    path('cart/', views.cart, name='cart'),
    path('newoffer/', views.newoffer, name='newoffer'),
    path('changeaccount/', views.changeaccount, name='changeaccount'),
    path('providerpage/', views.providerpage, name='providerpage'),
    path('<int:offer_id>/change/', views.changeoffer, name='changeoffer'),
    path('<int:offer_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('<int:offer_id>/remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path("signup/", views.signup, name="signup"),
    path("password/", password_change)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]