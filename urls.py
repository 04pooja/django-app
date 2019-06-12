


from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("products/<int:myid>", views.productview, name="ProductView"),
    path("search/",views.search,name="search"),
    path("checkout/", views.checkout, name="Checkout"),
    path("process/",views.process_payment,name="process_payment"),
    path("done/", views.payment_done, name="payment_done"),
    path("cancel/", views.payment_cancelled, name="payment_cancelled"),
   
]