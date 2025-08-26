""" Base serializers """

from rest_framework import serializers


class StatsSerializer(serializers.Serializer):
    """ Custom serializer used for StatsView """
    association_count = serializers.IntegerField()
    next_commission_date = serializers.DateField(allow_null=True)
    last_charter_update = serializers.DateField(allow_null=True)
