

from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('admin_login/',views.admin_login,name="admin_login"),
    path('admin_home/',views.admin_home,name="admin_home"),
    path('restaurants_details/',views.restaurants_details,name="restaurants_details"),
    path('delivery_details/',views.delivery_details,name="delivery_details"),
    path('sustainability_details/',views.sustainability_details,name="sustainability_details"),
    path('approve/<int:id>/', views.approve, name="approve"),
    path('rejection/<int:id>/', views.rejection, name="rejection"),
    path('r_approve/<int:id>/', views.r_approve, name="r_approve"),
    path('r_rejection/<int:id>/', views.r_rejection, name="r_rejection"),
    path('upload_stock/', views.upload_stock, name="upload_stock"),
    path('warehouse_stock/', views.warehouse_stock, name="warehouse_stock"),
    path('admin_logout/', views.admin_logout, name="admin_logout"),
    path('sus_report/', views.sus_report, name="sus_report"),
    path('f_approve/<int:id>/', views.f_approve, name="f_approve"),
    path('f_reject/<int:id>/', views.f_reject, name="f_reject"),


    ]