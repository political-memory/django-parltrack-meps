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

from datetime import date
from django.db import models
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify


CURRENT_MAGIC_VAL = date(9999, 12, 31)


class TimePeriodQueryset(models.query.QuerySet):
    def newer_first(self):
        return self.order_by('-end', '-begin')

    def only_current(self):
        return self.filter(end=CURRENT_MAGIC_VAL)

    def only_old(self):
        return self.filter(end__lt=CURRENT_MAGIC_VAL)

    def at_date(self, _date):
        return self.filter(begin__lt=_date, end__gt=_date)


class TimePeriodManager(models.Manager):
    use_for_related_fields = True

    def newer_first(self):
        return self.get_query_set().newer_first()

    def only_current(self):
        return self.get_query_set().only_current()

    def only_old(self):
        return self.get_query_set().only_old()

    def at_date(self, _date):
        return self.get_query_set().at_date(_date)

    def get_query_set(self):
        return TimePeriodQueryset(self.model)


class TimePeriod(models.Model):
    """
    Helper base class used on M2M intermediary models representing a
    relationship between a Representative and a Role (Group/Delegation/etc.)
    during a certain period in time.
    """
    class Meta:
        abstract = True

    objects = TimePeriodManager()

    begin = models.DateField(null=True)
    end = models.DateField(null=True)

    def is_current(self):
        if self.end == CURRENT_MAGIC_VAL:
            return True
        else:
            return False

    def is_past(self):
        if self.end < date.today():
            return True
        else:
            return False


class Country(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        return u"%s - %s" % (self.code, self.name)

    @property
    def meps(self):
        return self.mep_set.filter(active=True).distinct()

    def meps_on_date(self, date):
        return self.mep_set.filter(groupmep__end__gte=date, groupmep__begin__lte=date).distinct()

    class Meta:
        ordering = ["code"]


class Group(models.Model):
    abbreviation = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return u"%s - %s" % (self.abbreviation, self.name)
    content = __unicode__

    def get_absolute_url(self):
        return reverse('meps:index_by_group', args=(self.abbreviation,))

    @property
    def meps(self):
        return self.mep_set.filter(active=True).distinct()

    def meps_on_date(self, date):
        return self.mep_set.filter(groupmep__end__gte=date, groupmep__begin__lte=date).distinct()

    @classmethod
    def ordered_by_meps_count(cls):
        return cls.objects.distinct().filter(groupmep__mep__active=True).annotate(meps_count=Count('groupmep__mep', distinct=True)).order_by('-meps_count')


class Delegation(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name
    content = __unicode__

    def get_absolute_url(self):
        return reverse('meps:index_by_delegation', args=(self.id,))

    @property
    def meps(self):
        return self.mep_set.filter(active=True).distinct()


class Committee(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        return u"%s: %s" % (self.abbreviation, self.name)
    content = __unicode__

    def get_absolute_url(self):
        return reverse('meps:index_by_committee', args=(self.abbreviation,))

    @property
    def meps(self):
        return self.mep_set.filter(active=True).distinct()

    @classmethod
    def ordered_by_meps_count(cls):
        return cls.objects.distinct().filter(committeerole__mep__active=True).annotate(meps_count=Count('committeerole__mep', distinct=True)).order_by('-meps_count')


class Building(models.Model):
    """ A building of the European Parliament"""
    name = models.CharField(max_length=255)
    id = models.CharField('Abbreviation', max_length=255, primary_key=True)
    street = models.CharField(max_length=255)
    postcode = models.CharField(max_length=255)

    class Meta:
        ordering = ('postcode', 'pk',)

    def _town(self):
        return "bxl" if self.postcode == "1047" else "stg"

    def floors(self):
        floors = []

        def add(x):
            if getattr(x, "%s_floor" % self._town) not in floors:
                floors.append(getattr(x, "%s_floor" % self._town))
        map(add, self.meps.order_by("%s_floor" % self._town))
        return floors

    def meps(self):
        return getattr(self, "%s_building" % self._town).filter(active=True)

    def __unicode__(self):
        return u"%s - %s - %s - %s" % (self.id, self.name, self.street, self.postcode)


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name
    content = __unicode__

    def get_absolute_url(self):
        return reverse('meps:index_by_organization', args=(self.id,))

    @property
    def meps(self):
        return self.mep_set.filter(active=True).distinct()


class MEP(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=2, choices=((u'M', u'Male'), (u'F', u'Female')), null=True)
    birth_date = models.DateField(null=True)
    birth_place = models.CharField(max_length=255)
    active = models.BooleanField()
    ep_id = models.IntegerField(unique=True)
    ep_opinions = models.URLField()
    ep_debates = models.URLField()
    ep_questions = models.URLField()
    ep_declarations = models.URLField()
    ep_reports = models.URLField()
    ep_motions = models.URLField()
    ep_webpage = models.URLField()
    bxl_building = models.ForeignKey(Building, related_name="bxl_building", null=True)
    bxl_floor = models.CharField(max_length=255, null=True)
    bxl_office_number = models.CharField(max_length=255, null=True)
    bxl_fax = models.CharField(max_length=255, null=True)
    bxl_phone1 = models.CharField(max_length=255, null=True)
    bxl_phone2 = models.CharField(max_length=255, null=True)
    stg_building = models.ForeignKey(Building, related_name="stg_building", null=True)
    stg_floor = models.CharField(max_length=255, null=True)
    stg_office_number = models.CharField(max_length=255, null=True)
    stg_fax = models.CharField(max_length=255, null=True)
    stg_phone1 = models.CharField(max_length=255, null=True)
    stg_phone2 = models.CharField(max_length=255, null=True)
    groups = models.ManyToManyField(Group, through='GroupMEP')
    countries = models.ManyToManyField(Country, through='CountryMEP')
    delegations = models.ManyToManyField(Delegation, through='DelegationRole')
    committees = models.ManyToManyField(Committee, through='CommitteeRole')
    organizations = models.ManyToManyField(Organization, through='OrganizationMEP')
    total_score = models.FloatField(default=None, null=True)

    def age(self):
        if date.today().month > self.birth_date.month:
            return date.today().year - self.birth_date.year
        elif date.today().month == self.birth_date.month and date.today().day > self.birth_date.day:
            return date.today().year - self.birth_date.year
        else:
            return date.today().year - self.birth_date.year + 1

    def get_absolute_url(self):
        return reverse('meps:mep', args=(self.id,))

    def bxl_office(self):
        return self.bxl_floor + self.bxl_office_number

    def stg_office(self):
        return self.stg_floor + self.stg_office_number

    def group(self):
        return self.groupmep_set.select_related('group').latest('end').group if self.groupmep_set.count() else None

    def groupmep(self):
        return self.groupmep_set.self('group').latest('end')

    def country(self):
        return self.countrymep_set.select_related('country').latest('end').country

    def party(self):
        return self.countrymep_set.select_related('party').latest('end').party

    def previous_mandates(self):
        return self.countrymep_set.filter(end__isnull=False).order_by('-end')

    def current_delegations(self):
        return self.delegationrole_set.filter(end__isnull=True)

    def old_delegations(self):
        return self.delegationrole_set.filter(end__isnull=False).order_by('-end')

    def current_committees(self):
        return self.committeerole_set.filter(end__isnull=True)

    def old_committees(self):
        return self.committeerole_set.filter(end__isnull=False).order_by('-end')

    def current_organizations(self):
        return self.organizationmep_set.filter(end__isnull=True)

    def old_organizations(self):
        return self.organizationmep_set.filter(end__isnull=False).order_by('-end')

    def old_groups(self):
        return self.groupmep_set.filter(end__isnull=False).order_by('-end')

    def important_posts(self):
        all_roles = list(OrganizationMEP.objects.filter(mep=self).select_related('organization'))
        for i in (GroupMEP.objects.select_related('group').exclude(role="Member").exclude(role="Substitute"), CommitteeRole.objects.select_related('committee')):
            roles = i.filter(mep=self)
            if roles:
                all_roles += list(roles)
        return all_roles

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        ordering = ['last_name']


class NameVariation(models.Model):
    name = models.CharField(max_length=255)
    mep = models.ForeignKey(MEP)


class GroupMEP(TimePeriod):
    mep = models.ForeignKey(MEP)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=255)

    def instance(self):
        return self.group


class DelegationRole(TimePeriod):
    mep = models.ForeignKey(MEP)
    delegation = models.ForeignKey(Delegation)
    role = models.CharField(max_length=255)

    def instance(self):
        return self.delegation

    def __unicode__(self):
        return u"%s : %s" % (self.mep.full_name, self.delegation)


class CommitteeRole(TimePeriod):
    mep = models.ForeignKey(MEP)
    committee = models.ForeignKey(Committee)
    role = models.CharField(max_length=255)

    def instance(self):
        return self.committee

    def __unicode__(self):
        return u"%s : %s" % (self.committee.abbreviation, self.mep.full_name)


class PostalAddress(models.Model):
    addr = models.CharField(max_length=255)
    mep = models.ForeignKey(MEP)


class Party(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, null=True)

    def __unicode__(self):
        return self.name
    content = __unicode__

    def get_absolute_url(self):
        return reverse('meps:index_by_party', args=(self.id, slugify(self.name)))

    @property
    def meps(self):
        return MEP.objects.filter(partyrepresentative__party=self, active=True).distinct()


class CountryMEP(TimePeriod):
    mep = models.ForeignKey(MEP)
    country = models.ForeignKey(Country)
    party = models.ForeignKey(Party)


class OrganizationMEP(TimePeriod):
    mep = models.ForeignKey(MEP)
    organization = models.ForeignKey(Organization)
    role = models.CharField(max_length=255)


class Assistant(models.Model):
    full_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.full_name


class AssistantMEP(models.Model):
    mep = models.ForeignKey(MEP)
    assistant = models.ForeignKey(Assistant)
    type = models.CharField(max_length=255)


class Email(models.Model):
    email = models.EmailField()
    mep = models.ForeignKey(MEP)

    def __unicode__(self):
        return self.email


class CV(models.Model):
    title = models.TextField()
    mep = models.ForeignKey(MEP)

    def __unicode__(self):
        return self.title


class WebSite(models.Model):
    url = models.URLField()
    mep = models.ForeignKey(MEP)

    def __unicode__(self):
        return self.url or u'-'


class PartyMEP(models.Model):
    mep = models.ForeignKey(MEP)
    party = models.ForeignKey(Party)
    role = models.CharField(max_length=255, null=True)
    current = models.BooleanField()
