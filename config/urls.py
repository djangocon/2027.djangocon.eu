from django.conf import settings
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import RedirectView

from djangocon.site import views

urlpatterns = [
    path("", views.home, name="home"),
    # Legacy URL for the home page (linked from older material); one canonical URL is better for SEO.
    path("home/", RedirectView.as_view(url="/", permanent=True)),
    path("sponsors/sponsors/", views.sponsors, name="sponsors"),
    path("<slug:menu>/", views.page, name="page"),
    path("<slug:menu>/<slug:submenu>/", views.page, name="subpage"),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        path("403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")}),
        path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")}),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]
