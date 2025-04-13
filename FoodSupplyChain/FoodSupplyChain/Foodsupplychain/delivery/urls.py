from django.urls import path
from . import views

urlpatterns = [
    path('dl_register/',views.dl_register,name="dl_register"),
    path('dl_login/',views.dl_login,name="dl_login"),
    path('dl_home/',views.dl_home,name="dl_home"),
    path('DEl_report/', views.DEl_report, name="DEl_report"),

    path('Su_report/',views.Su_report,name="Su_report"),
    path('delivery_process/',views.delivery_process,name="delivery_process"),
    path('order/<int:id>/',views.order,name="order"),
    path('dl_logout/',views.dl_logout,name="dl_logout"),
    path('dl_approve/<int:id>/',views.dl_approve,name="dl_approve"),
    path('dl_reject/<int:id>/',views.dl_reject,name="dl_reject"),

    ]