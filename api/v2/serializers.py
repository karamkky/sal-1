from django.forms import widgets

from rest_framework import serializers

from api.v2.mixins import QueryFieldsMixin
from inventory.models import InventoryItem, Application
from profiles.models import *
from search.models import *
from server.models import *


class InventoryApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = '__all__'


class InventoryItemSerializer(serializers.ModelSerializer):

    application = InventoryApplicationSerializer()

    class Meta:
        model = InventoryItem
        fields = '__all__'


class BusinessUnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessUnit
        fields = '__all__'


class MachineGroupSerializer(serializers.ModelSerializer):
    business_unit = serializers.PrimaryKeyRelatedField(
        queryset=BusinessUnit.objects.all())

    class Meta:
        model = MachineGroup
        fields = '__all__'


class PluginScriptSubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PluginScriptSubmission
        fields = '__all__'


class PluginScriptRowSerializer(serializers.ModelSerializer):

    submission = PluginScriptSubmissionSerializer()

    class Meta:
        model = PluginScriptRow
        fields = '__all__'


class FactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Fact
        fields = '__all__'


class SerialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Machine
        fields = ('id', 'serial',)


class ManagementSourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ManagementSource
        fields = '__all__'


class ManagedItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = ManagedItem
        fields = '__all__'


class ManagedItemHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ManagedItemHistory
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'


# class MachineSerializer(QueryFieldsMixin, serializers.ModelSerializer):
class MachineSerializer(serializers.ModelSerializer):

    """
    Only used by saved_search and profiles
    TODO (sheagcraig): Make it possible to nest MachineSerializer with
    simple fields without using 'saved_search' kwarg
    """

    class Meta:
        model = Machine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """Modify the serializer's fields for saved_search.

        This is taken from the DRF Serializers: Dynamically Modifying
        Fields example to allow us to handle one case: during our
        conversion of the Queryset result of the Search module's
        search_machine method into json for API usage in the
        /api/saved_search/<id>/execute endpoint (which by default does
        not return the full results). This causes the serializer to
        freak out because there are not fields to serialize.
        """
        # There's probably a better way to do this.

        # Pop off special kwargs so they don't mess up the parent init.
        full_query = kwargs.pop('full', None)
        saved_search = kwargs.pop('saved_search', None)

        super(MachineSerializer, self).__init__(*args, **kwargs)

        # Only used by saved_search
        if saved_search and not full_query:
            # See sal/search/views.py for the source of the included
            # fields.
            allowed = {'id', 'serial', 'console_user', 'hostname', 'last_checkin'}
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class SearchRowSerializer(serializers.ModelSerializer):

    class Meta:
        model = SearchRow
        fields = '__all__'


class SearchGroupSerializer(serializers.ModelSerializer):
    search_rows = SearchRowSerializer(source='searchrow_set', read_only=True, many=True)

    class Meta:
        model = SearchGroup
        fields = '__all__'


class SavedSearchSerializer(serializers.ModelSerializer):
    search_groups = SearchGroupSerializer(source='searchgroup_set', read_only=True, many=True)

    class Meta:
        model = SavedSearch
        fields = '__all__'


class ProfilePayloadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payload
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):

    payloads = ProfilePayloadSerializer(source='payload_set', read_only=True, many=True)

    machine = MachineSerializer(full=False, saved_search=True)

    class Meta:
        model = Profile
        fields = '__all__'
