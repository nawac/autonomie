# -*- coding: utf-8 -*-
# * File Name : model.py
#
# * Copyright (C) 2012 Majerti <tech@majerti.fr>
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : mer. 11 janv. 2012
# * Last Modified : ven. 30 mars 2012 20:33:17 CEST
#
# * Project : autonomie
#
import datetime
import time

from hashlib import md5

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import Integer as Integer_type

from autonomie.models import DBBASE

class CustomeDateType(TypeDecorator):
    """
        Custom date type used because our database is using
        integers to store date's timestamp
    """
    impl = Integer_type
    def process_bind_param(self, value, dialect):
        if value is None:
            return int(time.time())
        elif isinstance(value, datetime.datetime):
            return int(time.mktime(value.timetuple()))
        elif isinstance(value, int):
            return value
        return time.mktime(value.timetuple())

    def process_result_value(self, value, dialect):
        if value:
            return datetime.datetime.fromtimestamp(float(value))
        else:
            return datetime.datetime.now()

def _get_date():
    """
        returns current time
    """
    return int(time.time())


company_employee = Table('coop_company_employee', DBBASE.metadata,
    Column("IDCompany", Integer(11), ForeignKey('coop_company.IDCompany')),
    # IDEmployee est identique dans la table coop_employee
    Column("IDEmployee", Integer(11), ForeignKey('egw_accounts.account_id')),
    autoload=True)

class Company(DBBASE):
    """
        `IDCompany` int(11) NOT NULL auto_increment,
        `name` varchar(150) NOT NULL,
        `object` varchar(255) NOT NULL,
        `email` varchar(255) default NULL,
        `phone` varchar(20) NOT NULL,
        `mobile` varchar(20) default NULL,
        `comments` text,
        `creationDate` int(11) NOT NULL,
        `updateDate` int(11) NOT NULL,
        `active` varchar(1) NOT NULL default 'Y',
        `IDGroup` int(11) NOT NULL,
        `logo` varchar(255) default NULL,
        `header` varchar(255) default NULL,
        `logoType` varchar(255) default NULL,
        `headerType` varchar(255) default NULL,
        `IDEGWUser` int(11) NOT NULL, # Company EGW account
        `RIB` varchar(255) default NULL,
        `IBAN` varchar(255) default NULL,
        PRIMARY KEY  (`IDCompany`)
    """
    __tablename__ = 'coop_company'
    __table_args__ = {'autoload':True}
    id = Column("IDCompany", Integer(11), primary_key=True)
    clients = relationship('Client',
                            order_by="Client.id",
                            backref='company')
    projects = relationship("Project",
                            order_by="Project.id",
                            backref="company")
    creationDate = Column("creationDate", CustomeDateType(11),
                                            default=_get_date)
    updateDate = Column("updateDate", CustomeDateType(11),
                                        default=_get_date,
                                        onupdate=_get_date)

    def get_client(self, client_id):
        """
            return the client with id (code) client_id
        """
        # Warn ! the id is a string
        for client in self.clients:
            if client.id == client_id:
                return client
        raise KeyError

    def get_project(self, project_id):
        """
            return the project with id project_id
        """
        if not isinstance(project_id, int):
            project_id = int(project_id)
        for project in self.projects:
            if project.id == project_id:
                return project
        raise KeyError

class User(DBBASE):
    """
        `account_id` int(11) NOT NULL auto_increment,
        `account_lid` varchar(64) NOT NULL,
        `account_pwd` varchar(100) NOT NULL,
        `account_firstname` varchar(50) default NULL,
        `account_lastname` varchar(50) default NULL,
        `account_lastlogin` int(11) default NULL,
        `account_lastloginfrom` varchar(255) default NULL,
        `account_lastpwd_change` int(11) default NULL,
        `account_status` varchar(1) NOT NULL default 'A',
        `account_expires` int(11) default NULL,
        `account_type` varchar(1) default NULL,
        `person_id` int(11) default NULL,
        `account_primary_group` int(11) NOT NULL default '0',
        `account_email` varchar(100) default NULL,
        `account_challenge` varchar(100) default NULL,
        `account_response` varchar(100) default NULL,
        PRIMARY KEY  (`account_id`),
        UNIQUE KEY `egw_accounts_account_lid` (`account_lid`)

    """
    __tablename__ = 'egw_accounts'
    __table_args__ = {'autoload':True}
    id = Column('account_id', Integer(11), primary_key=True)
    login = Column('account_lid', String(64))
    pwd = Column("account_pwd", String(100))
    lastname = Column("account_lastname", String(50))
    firstname = Column("account_firstname", String(50))
    email = Column("account_email", String(100))
    companies = relationship("Company", secondary=company_employee,
            backref="employees")

    @staticmethod
    def _encode_pass(password):
        return md5(password).hexdigest()

    def set_password(self, password):
        """
            Set the user's password
        """
        self.pwd = self._encode_pass(password)

    def auth(self, password):
        """
            Authentify the current record with password
        """
        if password:
            return self.pwd == self._encode_pass(password)
        else:
            return False

    def get_company(self, cid):
        """
            Return the company
        """
        if not isinstance(cid, int):
            cid = int(cid)
        for company in self.companies:
            if company.id == cid:
                return company
        raise KeyError

class Employee(DBBASE):
    """
        `IDEmployee` int(11) NOT NULL,
        `comments` text,
        `creationDate` int(11) NOT NULL,
        `updateDate` int(11) NOT NULL,
        `IDContact` int(11) default NULL,
        PRIMARY KEY  (`IDEmployee`)
    """
    __tablename__ = 'coop_employee'
    __table_args__ = {'autoload':True}
    id = Column("IDEmployee", Integer(11), primary_key=True)
    creationDate = Column("creationDate", CustomeDateType(11),
                                            default=_get_date)
    updateDate = Column("updateDate", CustomeDateType(11),
                                        default=_get_date,
                                        onupdate=_get_date)

class Task(DBBASE):
    """
        Metadata pour une tâche (estimation, invoice)
      `IDTask` int(11) NOT NULL auto_increment, #identifiant de la tâche
      `IDPhase` int(11) NOT NULL,           # identifiant de la phase associée
      `name` varchar(150) NOT NULL,         # Nom de la tâche
      `CAEStatus` varchar(10) default NULL,
      `customerStatus` varchar(10) default NULL,
      `taskDate` int(11) default '0',
      `IDEmployee` int(11) NOT NULL,
      `document` varchar(255) default NULL,
      `creationDate` int(11) NOT NULL,
      `updateDate` int(11) NOT NULL,
      `description` text,
      `statusComment` text,
      `documentType` varchar(255) default NULL,
      `statusPerson` int(11) default NULL,
      `statusDate` int(11) default NULL,
      `rank` int(11) default NULL,
      PRIMARY KEY  (`IDTask`),
      KEY `IDPhase` (`IDPhase`),
      KEY `IDEmployee` (`IDEmployee`)
    """
    __tablename__ = 'coop_task'
    __table_args__ = {'autoload':True}
    IDTask = Column(Integer, ForeignKey('coop_estimation.IDTask'),
                                                 primary_key=True)
    creationDate = Column("creationDate", CustomeDateType(11),
                                            default=_get_date)
    updateDate = Column("updateDate", CustomeDateType(11),
                                        default=_get_date,
                                        onupdate=_get_date)

class Estimation(DBBASE):
    """
       `IDTask` int(11) NOT NULL,
      `sequenceNumber` int(11) NOT NULL,
      `number` varchar(100) NOT NULL,
      `tva` int(11) NOT NULL default '196',
      `discount` int(11) NOT NULL default '0',
      `deposit` int(11) NOT NULL default '0',
      `paymentConditions` text,
      `exclusions` text,
      `IDProject` int(11) NOT NULL,
      `manualDeliverables` tinyint(4) default NULL,
      `course` tinyint(4) NOT NULL default '0',
      `displayedUnits` tinyint(4) NOT NULL default '0',
      `discountHT` int(11) NOT NULL default '0',
      `expenses` int(11) NOT NULL default '0',
      `paymentDisplay` varchar(20) default 'SUMMARY',
      PRIMARY KEY  (`IDTask`),
      KEY `coop_estimation_sequenceNumber` (`sequenceNumber`),
      KEY `coop_estimation_IDProject` (`IDProject`),
      KEY `IDProject` (`IDProject`)
    """
    __tablename__ = 'coop_estimation'
    __table_args__ = {'autoload':True}

    id = Column("IDTask", Integer(11), primary_key=True)
    lines = relationship("EstimationLine", backref="estimation")
    task = relationship("Task", backref="estimation", uselist=False)

class EstimationLine(DBBASE):
    """
      `IDWorkLine` int(11) NOT NULL auto_increment,
      `IDTask` int(11) NOT NULL,
      `rowIndex` int(11) NOT NULL,
      `description` text,
      `cost` int(11) default NULL,
      `quantity` double default NULL,
      `creationDate` int(11) default NULL,
      `updateDate` int(11) default NULL,
      `unity` varchar(10) default NULL,
      PRIMARY KEY  (`IDWorkLine`),
      KEY `coop_estimation_line_IDTask` (`IDTask`),
      KEY `coop_estimation_line_rowIndex` (`rowIndex`),
      KEY `IDTask` (`IDTask`)
    """
    __tablename__ = 'coop_estimation_line'
    __table_args__ = {'autoload':True}
    id = Column("IDWorkLine", Integer(11), primary_key=True)
    IDTask = Column(Integer, ForeignKey('coop_estimation.IDTask'))
    creationDate = Column("creationDate", CustomeDateType(11),
                                            default=_get_date)
    updateDate = Column("updateDate", CustomeDateType(11),
                                        default=_get_date,
                                        onupdate=_get_date)

class Client(DBBASE):
    """
       `code` varchar(4) NOT NULL,
        `IDContact` int(11) default '0',
        `comments` text,
        `creationDate` int(11) NOT NULL,
        `updateDate` int(11) NOT NULL,
        `IDCompany` int(11) NOT NULL,
        `intraTVA` varchar(50) default NULL,
        `address` varchar(255) default NULL,
        `zipCode` varchar(20) default NULL,
        `city` varchar(255) default NULL,
        `country` varchar(150) default NULL,
        `phone` varchar(50) default NULL,
        `email` varchar(255) default NULL,
        `contactLastName` varchar(255) default NULL,
        `name` varchar(255) default NULL,
        `contactFirstName` varchar(255) default NULL,
        PRIMARY KEY  (`code`),
        KEY `IDCompany` (`IDCompany`)
    """
    __tablename__ = 'coop_customer'
    __table_args__ = {'autoload':True}
    id = Column('code', String(4), primary_key=True)
    id_company = Column("IDCompany", Integer(11),
                                    ForeignKey('coop_company.IDCompany'))
    creationDate = Column("creationDate", CustomeDateType(11),
                                            default=_get_date)
    updateDate = Column("updateDate", CustomeDateType(11),
                                        default=_get_date,
                                        onupdate=_get_date)
    projects = relationship("Project", backref="client")

class Project(DBBASE):
    """
        `IDProject` int(11) NOT NULL auto_increment,
        `name` varchar(150) NOT NULL,
        `customerCode` varchar(4) NOT NULL,
        `type` varchar(150) default NULL,
        `code` varchar(4) NOT NULL,
        `definition` text,
        `creationDate` int(11) NOT NULL,
        `updateDate` int(11) NOT NULL,
        `startingDate` int(11) default NULL,
        `endingDate` int(11) default NULL,
        `status` varchar(20) NOT NULL,
        `IDCompany` int(11) NOT NULL,
        `dispatchType` varchar(10) NOT NULL default 'PERCENT',
        `archived` tinyint(4) NOT NULL default '0',
        PRIMARY KEY  (`IDProject`),
        KEY `IDCompany` (`IDCompany`)
    """
    __tablename__ = 'coop_project'
    __table_args__ = {'autoload':True}
    id = Column('IDProject', Integer(11), primary_key=True)
    id_company = Column("IDCompany", Integer(11),
                                    ForeignKey('coop_company.IDCompany'))
    code_client = Column("customerCode", String(4),
                                    ForeignKey('coop_customer.code'))
    creationDate = Column("creationDate", CustomeDateType(11),
                                            default=_get_date)
    updateDate = Column("updateDate", CustomeDateType(11),
                                        default=_get_date,
                                        onupdate=_get_date)
    startingDate = Column("startingDate", CustomeDateType(11),
                                            default=_get_date)
    endingDate = Column("endingDate", CustomeDateType(11),
                                            default=_get_date)
