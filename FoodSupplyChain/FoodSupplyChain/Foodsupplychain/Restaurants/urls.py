from django.urls import path
from . import views

urlpatterns = [
    path('re_register/',views.re_register,name="re_register"),
    path('re_login/',views.re_login,name="re_login"),
    path('re_home/',views.re_home,name="re_home"),
    path('add_card/',views.add_card,name="add_card"),
    path('cart/<str:Br_id>/',views.cart),
    path('add_price/<str:Br_id>/',views.cart),
    path('process_payment/',views.process_payment,name="process_payment"),
    path('payment/',views.payment,name="payment"),
    path('delete_item/<str:item_id>/', views.delete_item, name='delete_item'),
    path('order_details/', views.order_details, name='order_details'),
    path('res_logout/', views.res_logout, name='res_logout'),


    ]