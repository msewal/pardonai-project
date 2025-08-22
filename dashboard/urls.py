from django.urls import path
from django.shortcuts import render
from . import views
from .views_pareto import (
    api_pareto, api_pareto_topn, api_pareto_export, api_pareto_whatif
)

urlpatterns = [
    path('', views.dashboard_page, name='dashboard'),
    path("pareto/", lambda r: render(r, "dashboard/pareto.html"), name="pareto_page"),

    path("api/pareto", pareto.pareto_api, name="pareto_api"),
    path("api/pareto/topn", pareto.pareto_topn, name="pareto_topn"),
    path("api/pareto/abc", pareto.pareto_abc, name="pareto_abc"),
    path("api/pareto/lorenz", pareto.pareto_lorenz, name="pareto_lorenz"),
    path("api/pareto/scatter", pareto.pareto_scatter, name="pareto_scatter"),
    path("api/pareto/hist", pareto.pareto_hist, name="pareto_hist"),
    path("api/pareto/treemap", pareto.pareto_treemap, name="pareto_treemap"),
    path("api/pareto/whatif", pareto.pareto_whatif, name="pareto_whatif"),
    path("api/pareto/export", pareto.pareto_export, name="pareto_export"),
]