from django.urls import path
from . import views

urlpatterns = [
    path('su_register/',views.su_register,name="su_register"),
    path('su_login/',views.su_login,name="su_login"),
    path('su_home/',views.su_home,name="su_home"),
    path('order/',views.order,name="order"),
    path('su_encrypt/',views.su_encrypt,name="su_encrypt"),
    path('f_getkey/<str:id>/',views.f_getkey,name="f_getkey"),
    path('f_check_key/<str:id>/',views.f_check_key,name="f_check_key"),
    path('su_analyze/',views.su_analyze,name="su_analyze"),
    path('su_calculate/<str:id>/',views.su_calculate,name="su_calculate"),
    path('su_report/',views.su_report,name="su_report"),
    path('generate_pdf/<str:id>/', views.generate_pdf,name="generate_pdf"),
    path('su_logout/', views.su_logout,name="su_logout"),
    path('encrypt/', views.encrypt,name="encrypt"),
    path('s_analyze/', views.s_analyze,name="s_analyze"),
    path('report/', views.report,name="report"),

    ]