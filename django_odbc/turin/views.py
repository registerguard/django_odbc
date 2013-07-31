from django.shortcuts import render

def today(request):
    return render(request, 'turin/base.html')
