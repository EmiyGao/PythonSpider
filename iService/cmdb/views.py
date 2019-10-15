from django.shortcuts import render
from django.shortcuts import HttpResponse
from cmdb import models
# Create your views here.


def enquery(request):

    if request.method =="POST":
        u = request.POST.get('select')
        v = request.POST.get('values')
        print(u,v)
        if u == 'number':
            user_list = models.result.objects.filter(Population=v)
            print('number')
        if u == 'name':
            user_list = models.result.objects.filter(Name=v)
            print('name')
        if u == 'cin':
            user_list = models.result.objects.filter(District=v)
            print('cin')
        # models.Tb1.objects.filter(name='seven')
        if u == 'all':
            user_list = models.result.objects.all()
            print('all')
        print(user_list)
        # user_list = [{'seq':'1','number':'dsakjdhadh','name':'emiy','GHO':'PRS'},
        #              {'seq': '2', 'number': 'dsakjdhadh', 'name': 'ccc', 'GHO': 'PRS'},
        #              {'seq': '3', 'number': 'dsakjdhadh', 'name': 'bbb', 'GHO': 'PRS'},
        #              {'seq': '4', 'number': 'dsakjdhadh', 'name': 'aaa', 'GHO': 'PRS'}
        #              ]
        return render(request, 'home.html', {'rst_list':user_list})
    return render(request, 'First.html')

