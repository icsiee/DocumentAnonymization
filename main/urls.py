from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import yazar_sayfasi


urlpatterns = [
    path('', views.yazar_sayfasi, name='yazar_sayfasi'),
    path('yazar/', yazar_sayfasi, name='yazar_sayfasi'),
path('editor/', views.editor_page, name='editor_page'),
    path('reviewer/', views.reviewer_page, name='reviewer_page'),


]

# Media dosyalarını erişilebilir yapmak
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
