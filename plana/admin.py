"""Admin home page."""
from django.contrib import admin
from django.contrib.admin import sites


class CustomAdminSite(admin.AdminSite):
    """Admin home page."""

    def get_app_list(self, request, app_label=None):
        """Sort applications in admin menu."""
        apps_order = {
            "history": 1,
            "contents": 2,
            "mail_template": 3,
            "users": 4,
            "associations": 5,
            "institutions": 6,
            "commissions": 7,
            "projects": 8,
            "documents": 9,
        }
        models_order = {
            "History": 1,
            "Content": 2,
            "Logo": 3,
            "MailTemplate": 4,
            "User": 5,
            "GroupInstitutionFundUser": 6,
            "AssociationUser": 7,
            "Association": 8,
            "ActivityField": 9,
            "Institution": 10,
            "InstitutionComponent": 11,
            "Fund": 12,
            "Commission": 13,
            "CommissionFund": 14,
            "Project": 15,
            "Category": 16,
            "ProjectCategory": 17,
            "ProjectCommissionFund": 18,
            "ProjectComment": 19,
            "Document": 20,
            "DocumentUpload": 21,
        }

        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: apps_order[x["app_label"]])

        for app in app_list:
            app["models"].sort(key=lambda x: models_order[x["object_name"]])

        return app_list


custom_site = CustomAdminSite()
admin.site = custom_site
sites.site = custom_site
