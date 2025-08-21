from django.shortcuts import render

def dashboard_page(request):
    return render(request, "dashboard/dashboard.html")

def pareto_page(request):
    return render(request, "pareto.html")