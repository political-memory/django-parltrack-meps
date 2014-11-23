# encoding: utf-8

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
# Copyright (C) 2014  stf <s@ctrlc.hu>

import os
import sys
import json
from os.path import join
from datetime import datetime
import urllib

from guess_language import guessLanguage
from lxml import etree

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db import transaction

from parltrack_meps.models import (Party, MEP, Committee, Dossier, Amendment)

# XXX
JSON_DUMP_ARCHIVE_LOCALIZATION = join("/tmp", "ep_amendments.json.xz")
JSON_DUMP_LOCALIZATION = join("/tmp", "ep_amendments.json")
CURRENT_TERM = 8
_parse_date = lambda date: datetime.strptime(date, "%Y-%m-%dT00:%H:00")

def get_or_create(klass, _id=None, **kwargs):
    if _id is None:
        object = klass.objects.filter(**kwargs)
    else:
        object = klass.objects.filter(**{_id: kwargs[_id]})
    if object:
        return object[0]
    else:
        # print "     add new", klass.__name__, kwargs
        return klass.objects.create(**kwargs)

def ptjson(path):
    with open(path, "r") as fd:
        fd.read(1) # skip leading [
        for line in fd:
            if line.strip() == ',': continue
            if line.strip() == ']': return
            yield json.loads(line)

class Command(BaseCommand):
    help = 'Update the amendment data by pulling it from parltrack'

    @transaction.non_atomic_requests
    def handle(self, *args, **options):
        #if os.system("which unxz > /dev/null") != 0:
        #    raise Exception("unxz binary missing, please install xz")
        #print "clean old downloaded files"
        #if os.path.exists(JSON_DUMP_ARCHIVE_LOCALIZATION):
        #    os.remove(JSON_DUMP_ARCHIVE_LOCALIZATION)
        #if os.path.exists(JSON_DUMP_LOCALIZATION):
        #    os.remove(JSON_DUMP_LOCALIZATION)
        #print "download lastest data dump of amendments from parltrack"
        #urllib.urlretrieve('http://parltrack.euwiki.org/dumps/ep_amendments.json.xz', JSON_DUMP_ARCHIVE_LOCALIZATION)
        #print "unxz dump"
        #os.system("unxz %s" % JSON_DUMP_ARCHIVE_LOCALIZATION)
        #print "load json"
        #with transaction.commit_on_success():
        transaction.set_autocommit(False)
        total = 0
        for am in ptjson(JSON_DUMP_LOCALIZATION):
            if not 'date' in am or _parse_date(am['date'])<datetime(2014,7,1,0,0):
                continue
            for eid in am.get('meps',[]):
                try:
                    mep = MEP.objects.get(ep_id=eid)
                except MEP.DoesNotExist:
                    #print 'momep'
                    continue
                if not mep.active:
                    #print 'mehmep'
                    continue
                try:
                    doc = Dossier.objects.get(reference=am['reference'])
                except Dossier.DoesNotExist:
                    #print 'nodoc'
                    continue
                #print mep.full_name, doc.reference, am['seq']
                obj = get_or_create(Amendment,
                                    dossier = doc,
                                    new='\n'.join(am['new']),
                                    old='\n'.join(am.get('old',[])),
                                    url=am['src'],
                                    seq=am['seq'],
                                    date=_parse_date(am['date']),
                                    location=' // '.join(am['location'][0]))
                obj.save()
                obj.meps.add(mep)
                for com in am['committee']:
                    c = Committee.objects.get(abbreviation = com)
                    obj.committees.add(c)
            if (total % 100) == 0:
                sys.stdout.write('\r%s' % total)
                sys.stdout.flush()
            total+=1
            transaction.commit()
        print

# vim:set shiftwidth=4 tabstop=4 expandtab:
