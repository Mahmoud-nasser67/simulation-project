from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .graph import render_chart
urlpatterns = [
    path('add_customers/<int:server_id>/', views.add_customers, name='add_customers'),
    path('graph/', views.render_chart, name='render_chart'),
    path('details_server1/', views.one_serves,name='details_server1'),
    path('', views.index,name='index'),
    path('details_server2/', views.details_server2,name='details_server2'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)