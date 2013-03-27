# This file is part of django-parltrack-meps.
#
# Foobar is free software: you can redistribute it and/or modify
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

from django.contrib import admin

from memopol.reps.models import Party
from .models import CountryMEP, GroupMEP, DelegationRole
from .models import Committee, Delegation, Country, Group, MEP, CommitteeRole

admin.site.register(Committee)
admin.site.register(CommitteeRole)
admin.site.register(Delegation)
admin.site.register(DelegationRole)
admin.site.register(Country)
admin.site.register(Group)
admin.site.register(Party)

class CountriesInline(admin.TabularInline):
    model = CountryMEP
    extra = 1

class GroupInline(admin.TabularInline):
    model = GroupMEP
    extra = 1

class DelegationInline(admin.TabularInline):
    model = DelegationRole
    extra = 1

class CommitteeInline(admin.TabularInline):
    model = CommitteeRole
    extra = 1

class MEPAdmin(admin.ModelAdmin):
    search_fields = ['last_name']
    list_filter = ('active', 'countries', 'groups')
    list_display = ('last_name', 'first_name', 'active')
    inlines = [CountriesInline, GroupInline, DelegationInline, CommitteeInline]

admin.site.register(MEP, MEPAdmin)
