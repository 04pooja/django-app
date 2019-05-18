
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name="homeshop"),
    path('about/',views.about, name="aboutus"),
    path('contact/',views.contact, name="contactus"),
    path('tracker/',views.tracker, name="trackingstatus"),
    path('products/<int:myid>',views.productview, name="productview"),
    path('checkout/',views.checkout, name="checkout"),
    path('handlerequest/',views.handlerequest, name="handlerequest"),
]