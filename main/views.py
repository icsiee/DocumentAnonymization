from django.shortcuts import render

from django.shortcuts import render

from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponse
from .forms import MakaleForm


def yazar_sayfasi(request):
    if request.method == 'POST':
        # Formu işleyin ve dosyayı kaydedin
        email = request.POST.get('email')
        makale = request.FILES.get('makale')

        # Veritabanına veya dosya sistemine kaydetme işlemi burada yapılabilir
        # Örneğin, dosya bir yerde saklanabilir

        return HttpResponse("Makale başarıyla yüklendi!")

    return render(request, 'yazar.html')

# Create your views here.
