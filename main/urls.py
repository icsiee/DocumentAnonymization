from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import pdf_goruntule_hakem  # Görüntüleme fonksiyonunu içe aktar

from .views import *


urlpatterns = [
    path('', views.yazar_sayfasi, name='yazar_sayfasi'),
    path('yazar/', yazar_sayfasi, name='yazar_sayfasi'),
    path('makale_yukle/', views.makale_yukle, name='makale_yukle'),
    path('makale_durum_sorgulama/', views.makale_durum_sorgulama, name='makale_durum_sorgulama'),
    path('editor/', views.editor_page, name='editor_page'),
    path('reviewer/', views.reviewer_page, name='reviewer_page'),
    path('review/<int:article_id>/', views.review_article, name='degerlendir'),
    path('delete_article/<int:article_id>/', delete_article, name='delete_article'),
    path('send_message/', views.send_message, name='send_message'),
    path('delete_all_articles/', views.delete_all_articles, name='delete_all_articles'),
    path('makale/revize/<int:article_id>/', views.revize_et, name='revize_et'),
    path('encrypt_article/<int:article_id>/', views.encrypt_article, name='encrypt_article'),
    path('download_encrypted_pdf/<int:article_id>/', views.download_encrypted_pdf, name='download_encrypted_pdf'),
    path('<str:hakem_username>/', views.hakem_page, name='hakem_page'),
    path('create_reviewers_and_assign_topics/', views.create_reviewers_and_assign_topics,
                       name='create_reviewers_and_assign_topics'),
    path('makale/pdf/<int:tracking_number>/', views.pdf_goruntule, name='pdf_goruntule'),
    path('send/<int:article_id>/', views.send_article_view, name='send_article'),
    path('assign_reviewer/<int:article_id>/<int:reviewer_id>/', views.assign_reviewer, name='assign_reviewer'),
    path('log_panel/', views.log_panel, name='log_panel'),
    path('create_reviewers_and_assign_topics/', views.create_reviewers_and_assign_topics, name='create_reviewers_and_assign_topics'),
                  path('indir/<str:tracking_number>/', pdf_indir, name='pdf_indir'),
                  path('makale_sil/<int:article_id>/', makale_sil, name='makale_sil'),
                  path('makale/sifreli/<str:tracking_number>/', pdf_goruntule_hakem, name='pdf_goruntule_hakem'),
                  path('review_article/<int:article_id>/', views.review_article, name='add_review'),
                  # Burada 'article_id' kullanılıyor
                  # Değerlendirme ekleme URL'si

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Media dosyalarına erişim için ekleme
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
