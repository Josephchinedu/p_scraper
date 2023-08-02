from django.urls import path

from scraper.views import LoginView, RegisterView, WebScraperView

ACCOUNT_URLS = [
    path("account/register/", RegisterView.as_view(), name="register"),
    path("account/login/", LoginView.as_view(), name="login"),
]


SCRAPER_URLS = [
    path("scrape/", WebScraperView.as_view(), name="scrape"),
]


urlpatterns = [
    *ACCOUNT_URLS,
    *SCRAPER_URLS,
]
