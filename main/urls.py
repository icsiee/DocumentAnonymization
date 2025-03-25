from django.urls import path
from . import views  # Doğru kullanım
from django.conf import settings
from django.conf.urls.static import static

from .views import yazar_sayfasi, generate_random_reviewers, pdf_goruntule, delete_article

urlpatterns = ([
    path('', views.yazar_sayfasi, name='yazar_sayfasi'),
    path('yazar/', yazar_sayfasi, name='yazar_sayfasi'),
    path('makale_yukle/', views.makale_yukle, name='makale_yukle'),  # Yeni URL ekleyin
    path('makale_durum_sorgulama/', views.makale_durum_sorgulama, name='makale_durum_sorgulama'),
    path('editor/', views.editor_page, name='editor_page'),
    path('reviewer/', views.reviewer_page, name='reviewer_page'),
    path('reviewer/', views.reviewer_page, name='reviewer_page'),
    path('review/<int:article_id>/', views.review_article, name='degerlendir'),
    path('delete_article/<int:article_id>/', delete_article, name='delete_article'),
    path('send_message/', views.send_message, name='send_message'),
    path('delete_all_articles/', views.delete_all_articles, name='delete_all_articles'),
    path('makale/revize/<int:article_id>/', views.revize_et, name='revize_et'),  # Makale ID'si ile revize etme sayfasına yönlendir
    path('assign-reviewers/', generate_random_reviewers, name='assign_reviewers'),
                   path('makale/pdf/<int:article_id>/', pdf_goruntule, name='pdf_goruntule'),
path('encrypt_article/<int:article_id>/', views.encrypt_article, name='encrypt_article'),
                   path('view_encrypted_article/<int:article_id>/', views.view_encrypted_article,
                        name='view_encrypted_article'),
                   path('download_encrypted_article/<int:article_id>/', views.download_encrypted_article,
                        name='download_encrypted_article'),

               ]
   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))

# Media dosyalarını erişilebilir yapmak
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
