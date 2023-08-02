from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from scraper.models import ScrapedData


# Register your models here.
class ScrapedDataResource(resources.ModelResource):
    class Meta:
        model = ScrapedData


class ScrapedDataResourceAdmin(ImportExportModelAdmin):
    resource_class = ScrapedDataResource
    search_fields = [
        "user__email",
        "user__username",
        "user__first_name",
        "user__last_name",
    ]
    list_filter = ("created_at",)
    date_hierarchy = "created_at"

    raw_id_fields = ["user"]

    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]


admin.site.register(ScrapedData, ScrapedDataResourceAdmin)
