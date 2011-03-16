######################################################################
#
#  DSS2TP-to-ST.py.  Transfers time-accounting information from the
#  DSS database to the DSS_TP_to_ST MySQL database that will be then
#  read by Carl's code to produce time-accounting reports.
#
#  Copyright (C) 2009 Associated Universities, Inc. Washington DC, USA.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Correspondence concerning GBT software should be addressed as follows:
#  GBT Operations
#  National Radio Astronomy Observatory
#  P. O. Box 2
#  Green Bank, WV 24944-0002 USA
#
#  $Id:$
#
######################################################################
from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler.models import *
from datetime        import datetime, timedelta
import math
import MySQLdb as m
import pytz


UTC = pytz.timezone('UTC')
EST = pytz.timezone('US/Eastern')

dbhost = "leo.gb.nrao.edu"
dbuser = "dss"
dbpasswd = "asdf5!"
database = "DSS_TP_to_ST"
silent   = True

projects_table_sql = \
"""
CREATE TABLE `projects` (
  `id` int(11) not null,
  `pcode` varchar(64) not null,
  `name` varchar(256) default null,
  PRIMARY KEY (`id`)
)
"""

sessions_table_sql = \
"""
CREATE TABLE `sessions` (
  `id` int(11) not null auto_increment,
  `project_id` int(11) not null,
  `name` varchar(128) default null,
  `original_id` int(11) default null,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`)
)
"""

sessions_receiver_table_sql =  \
"""
CREATE TABLE `session_receivers` (
  `session_id` int(11) default NULL,
  `receiver_id` int(11) default NULL,
  KEY `session_id` (`session_id`),
  KEY `receiver_id` (`receiver_id`)
)
"""

receivers_table_sql =  \
"""
CREATE TABLE `receivers` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(32) default NULL,
  PRIMARY KEY  (`id`)
)
"""

periods_table_sql = \
"""
CREATE TABLE `periods` (
  `id` int(11) NOT NULL auto_increment,
  `session_id` int(11) default NULL,
  `start_time` datetime default NULL,
  `duration` varchar(32) default NULL,
  `completed_hours` varchar(32) default NULL,
  PRIMARY KEY  (`id`),
  KEY `session_id` (`session_id`)
)
"""

db = m.connect(host = dbhost, user = dbuser, passwd = dbpasswd)
cursor = db.cursor()

def utc2est(dt):
    if dt.tzname() != 'UTC':
        raise "Attempt to convert a non-UTC timestamp!"

    return dt.astimezone('EST')


def drop_database():
    cursor.execute("drop database if exists `%s`" % database)

def create_database():
    cursor.execute("create database if not exists `%s`" % database);
    db.select_db(database)
    cursor.execute(projects_table_sql)
    cursor.execute(sessions_table_sql)
    cursor.execute(sessions_receiver_table_sql)
    cursor.execute(receivers_table_sql)
    cursor.execute(periods_table_sql)


def transfer_projects():
    for i in Project.objects.all():
        cursor.execute("INSERT INTO `projects` (`id`, `pcode`) VALUES(%d, \"%s\")" \
                       % (i.id, i.pcode))


def transfer_sessions():
    for i in Sesshun.objects.all():
        
        if i.original_id:
            cursor.execute("""INSERT INTO `sessions`
                                (`id`, `project_id`, `name`, `original_id`)
                                VALUES (%d, %d, \"%s\", %d)""" \
                       % (i.id, i.project_id, i.name, i.original_id))
        else:
            cursor.execute("""INSERT INTO `sessions`
                                (`id`, `project_id`, `name`)
                                VALUES (%d, %d, \"%s\")""" \
                       % (i.id, i.project_id, i.name))
            

def transfer_session_receivers():

    session_receivers = {}

    for i in Receiver_Group.objects.all():

        session_receivers[i.session_id] = set()

        for j in i.receivers.all():
            session_receivers[i.session_id].add(j.id)

    for i in session_receivers:
        for j in session_receivers[i]:
            cursor.execute("""INSERT INTO `session_receivers`
                                (`session_id`, `receiver_id`) VALUES (%d, %d)""" \
                           % (i, j))


def transfer_receivers():
    for i in Receiver.objects.all():
        cursor.execute("INSERT INTO `receivers` (`id`, `name`) VALUES (%d, \"%s\")" \
                       % (i.id, i.name))


def transfer_periods():

    for i in Period.objects.all():

        if i.state.abbreviation == 'D':
            continue
        
        completed_hours_string = str(i.accounting.time_billed())
        start_ut = i.start.replace(tzinfo = UTC)
        stop_ut = i.end().replace(tzinfo = UTC)
        start_et = start_ut.astimezone(EST);
        stop_et = stop_ut.astimezone(EST);
        delta = stop_et - start_et
        duration = str(delta.days * 24.0 + delta.seconds / 3600.0)

        print start_et, stop_et, duration
                  
        cursor.execute("""INSERT INTO `periods`
                            (`id`, `session_id`, `start_time`, `duration`, `completed_hours`)
                            VALUES (%d, %d, \"%s\", \"%s\", \"%s\")""" \
                       % (i.id, i.session_id, start_et.replace(tzinfo = None), duration, completed_hours_string))


if __name__ == "__main__":
    drop_database()
    create_database()
    transfer_projects()
    transfer_sessions()
    transfer_session_receivers()
    transfer_receivers()
    transfer_periods()
