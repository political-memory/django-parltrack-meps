# This file is part of django-parltrack-meps.
#
# django-parltrack-meps is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or any later version.
#
# django-parltrack-meps is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU General Affero Public
# License along with Foobar.
# If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2013  Laurent Peuch <cortex@worlddomination.be>

from tastypie import fields
from tastypie.resources import ModelResource
from parltrack_meps.models import Country,\
                                LocalParty,\
                                Group,\
                                Delegation,\
                                Committee,\
                                Building,\
                                Organization,\
                                MEP,\
                                GroupMEP,\
                                DelegationRole,\
                                CommitteeRole,\
                                PostalAddress,\
                                CountryMEP,\
                                OrganizationMEP


class MEPCountryResource(ModelResource):
    countrymep_set = fields.ToManyField("parltrack_meps.api.MEPCountryMEPResource", "countrymep_set")

    class Meta:
        queryset = Country.objects.all()


class MEPLocalPartyResource(ModelResource):
    countrymep_set = fields.ToManyField("parltrack_meps.api.MEPCountryMEPResource", "countrymep_set")
    country = fields.ForeignKey(MEPCountryResource, "country")

    class Meta:
        queryset = LocalParty.objects.all()


class MEPGroupResource(ModelResource):
    groupmep_set = fields.ToManyField("parltrack_meps.api.MEPGroupMEPResource", "groupmep_set")
    class Meta:
        queryset = Group.objects.all()


class MEPDelegationResource(ModelResource):
    delegationrole_set = fields.ToManyField("parltrack_meps.api.MEPDelegationRoleResource", "delegationrole_set")

    class Meta:
        queryset = Delegation.objects.all()


class MEPCommitteeResource(ModelResource):
    committeerole_set = fields.ToManyField("parltrack_meps.api.MEPCommitteeRoleResource", "committeerole_set")

    class Meta:
        queryset = Committee.objects.all()


class MEPBuildingResource(ModelResource):
    class Meta:
        queryset = Building.objects.all()


class MEPOrganizationResource(ModelResource):
    organizationmep_set = fields.ToManyField("parltrack_meps.api.MEPOrganizationMEPResource", "organizationmep_set")

    class Meta:
        queryset = Organization.objects.all()


class MEPMEPResource(ModelResource):
    bxl_building = fields.ForeignKey(MEPBuildingResource, "bxl_building")
    stg_building = fields.ForeignKey(MEPBuildingResource, "stg_building")
    countrymep_set = fields.ToManyField("parltrack_meps.api.MEPCountryMEPResource", "countrymep_set")
    groupmep_set = fields.ToManyField("parltrack_meps.api.MEPGroupMEPResource", "groupmep_set")
    delegationrole_set = fields.ToManyField("parltrack_meps.api.MEPDelegationRoleResource", "delegationrole_set")
    committeerole_set = fields.ToManyField("parltrack_meps.api.MEPCommitteeRoleResource", "committeerole_set")
    organizationmep_set = fields.ToManyField("parltrack_meps.api.MEPOrganizationMEPResource", "organizationmep_set")

    class Meta:
        queryset = MEP.objects.all()


class MEPGroupMEPResource(ModelResource):
    group = fields.ForeignKey(MEPGroupResource, "group")
    mep = fields.ForeignKey(MEPMEPResource, "mep")

    class Meta:
        queryset = GroupMEP.objects.all()


class MEPDelegationRoleResource(ModelResource):
    mep = fields.ForeignKey(MEPMEPResource, "mep")
    delegation = fields.ForeignKey(MEPDelegationResource, "delegation")

    class Meta:
        queryset = DelegationRole.objects.all()


class MEPCommitteeRoleResource(ModelResource):
    mep = fields.ForeignKey(MEPMEPResource, "mep")
    committee = fields.ForeignKey(MEPCommitteeResource, "committee")

    class Meta:
        queryset = CommitteeRole.objects.all()


class MEPPostalAddressResource(ModelResource):
    mep = fields.ForeignKey(MEPMEPResource, "mep")

    class Meta:
        queryset = PostalAddress.objects.all()


class MEPCountryMEPResource(ModelResource):
    mep = fields.ForeignKey(MEPMEPResource, "mep")
    country = fields.ForeignKey(MEPCountryResource, "country")
    party = fields.ForeignKey(MEPLocalPartyResource, "party")

    class Meta:
        queryset = CountryMEP.objects.all()


class MEPOrganizationMEPResource(ModelResource):
    mep = fields.ForeignKey(MEPMEPResource, "mep")
    organization = fields.ForeignKey(MEPOrganizationResource, "organization")

    class Meta:
        queryset = OrganizationMEP.objects.all()
