from django.http import HttpResponseRedirect
from django.urls import reverse

def authentication_middleware(get_response):
    def middleware(request):
        if request.path in ['/home/', '/second/', '/official_home/']:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('index_view'))
        return get_response(request)
    return middleware
