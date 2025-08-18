from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def search(request):
    results = request.session.pop('result', None)


    return render(request, 'search.html', {'results' : results})