"""Filters for users app views"""

from django_filters import rest_framework as filters
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class UserFilter(filters.FilterSet):
    name = filters.CharFilter(method="filter_name")
    email = filters.CharFilter(method="filter_email")
    is_cas = filters.BooleanFilter(method="filter_is_cas")
    association_id = filters.NumberFilter(field_name="associations__id", lookup_expr="exact")

    class Meta:
        model = User
        fields = ["is_validated_by_admin", "name", "email", "is_cas", "association_id"]

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__nospaces__unaccent__icontains=value.strip().replace(" ", ""))
            | Q(last_name__nospaces__unaccent__icontains=value.strip().replace(" ", ""))
        )

    def filter_email(self, queryset, name, value):
        return queryset.filter(email__nospaces__unaccent__icontains=value.strip().replace(" ", ""))

    def filter_is_cas(self, queryset, name, value):
        cas_ids_list = SocialAccount.objects.filter(provider="cas").values_list("user_id", flat=True)
        if value:
            return queryset.filter(id__in=cas_ids_list)
        else:
            return queryset.exclude(id__in=cas_ids_list)

#class AssociationUserFilter(filters.FilterSet):
#    #association_id = filters.NumberFilter(method='filter_association_id')
#
#    #def filter_association_id(self, queryset, name, value):
#    #    if (
#    #        value
#    #        and (
#    #            self.request.user.has_perm("users.view_associationuser_anyone")
#    #            or self.request.user.is_president_in_association(value)
#    #        )
#    #    ):
#    #        return queryset.filter(association_id=value)
#    #    return queryset
#
#    class Meta:
#        model = AssociationUser
#        fields = [
#            "is_validated_by_admin",
#            #"association_id"
#        ]
