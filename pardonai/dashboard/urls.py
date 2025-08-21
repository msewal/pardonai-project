from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path("", views.dashboard_page, name="dashboard_page"),  # Ana sayfa
    path("dashboard/", views.dashboard_page, name="dashboard_page"),
    path("test/", views.test_page, name="test_page"),  # Test sayfası
    path("pareto/", views.pareto_page, name="pareto_page"),

    # APIs
    path("api/pareto", views.pareto_api, name="pareto_api"),
    path("api/pareto/topn", views.pareto_topn_api, name="pareto_topn_api"),
    path("api/pareto/export", views.pareto_export_csv, name="pareto_export_csv"),
    path("api/pareto/whatif", views.pareto_whatif_api, name="pareto_whatif_api"),
]
