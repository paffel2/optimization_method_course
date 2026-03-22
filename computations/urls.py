from django.urls import path
from computations.views import (
    ComputationCreateView,
    ComputationResultsView,
    LoginView,
    LogoutView,
    IndexView,
    ComputationListView,
)


app_name = "computations"

urlpatterns = [
    path("input/", ComputationCreateView.as_view(), name="input"),
    path("result/<int:pk>", ComputationResultsView.as_view(), name="result"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", IndexView.as_view(), name="index"),
    path("results/", ComputationListView.as_view(), name="results"),
]
