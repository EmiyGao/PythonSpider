from django.shortcuts import render
from django.shortcuts import HttpResponse
# Create your views here.


def enquery(request):
    if request.method =="POST":
        u = request.POST.get('select')
        v = request.POST.get('values')
        print(u,v)
        user_list = [{'seq':'1','number':'dsakjdhadh','name':'emiy','GHO':'PRS'},
                     {'seq': '2', 'number': 'dsakjdhadh', 'name': 'ccc', 'GHO': 'PRS'},
                     {'seq': '3', 'number': 'dsakjdhadh', 'name': 'bbb', 'GHO': 'PRS'},
                     {'seq': '4', 'number': 'dsakjdhadh', 'name': 'aaa', 'GHO': 'PRS'}
                     ]
        return render(request, 'home.html', {'rst_list':user_list})
    return render(request, 'First.html')

