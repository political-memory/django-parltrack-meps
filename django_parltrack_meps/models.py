from datetime import date
from django.db import models
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify


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

    class Meta:
        ordering = ['last_name']


class GroupMEP(models.Model):
    mep = models.ForeignKey(MEP)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=255)
    begin = models.DateField(null=True)
    end = models.DateField(null=True)

    def instance(self):
        return self.group


class DelegationRole(models.Model):
    mep = models.ForeignKey(MEP)
    delegation = models.ForeignKey(Delegation)
    role = models.CharField(max_length=255)
    begin = models.DateField(null=True)
    end = models.DateField(null=True)

    def instance(self):
        return self.delegation

    def __unicode__(self):
        return u"%s : %s" % (self.mep.full_name, self.delegation)


class CommitteeRole(models.Model):
    mep = models.ForeignKey(MEP)
    committee = models.ForeignKey(Committee)
    role = models.CharField(max_length=255)
    begin = models.DateField(null=True)
    end = models.DateField(null=True)

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


class CountryMEP(models.Model):
    mep = models.ForeignKey(MEP)
    country = models.ForeignKey(Country)
    party = models.ForeignKey(Party)
    begin = models.DateField(null=True)
    end = models.DateField(null=True)


class OrganizationMEP(models.Model):
    mep = models.ForeignKey(MEP)
    organization = models.ForeignKey(Organization)
    role = models.CharField(max_length=255)
    begin = models.DateField(null=True)
    end = models.DateField(null=True)


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
