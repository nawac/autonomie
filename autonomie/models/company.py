# -*- coding: utf-8 -*-
# * File Name : company.py
#
# * Copyright (C) 2010 Gaston TJEBBES <g.t@majerti.fr>
# * Company : Majerti ( http://www.majerti.fr )
#
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 25-07-2012
# * Last Modified :
#
# * Project :
#
"""
    Company model
"""
import os
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import deferred

from autonomie.models.utils import get_current_timestamp
from autonomie.models.types import CustomDateType
from autonomie.models.types import CustomFileType

from autonomie.models import DBBASE
from autonomie.models import DBSESSION

log = logging.getLogger(__name__)


class Company(DBBASE):
    """
        Company model
        Store all company specific stuff (headers, logos, RIB, ...)
    """
    __tablename__ = 'company'
    __table_args__ = {'mysql_engine': 'MyISAM', "mysql_charset": 'utf8'}
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(150))
    goal = deferred(Column("object", String(255)),
            group='edit')
    email = deferred(Column("email", String(255)),
            group='edit')
    phone = deferred(Column("phone", String(20), default=""),
            group='edit')
    mobile = deferred(Column("mobile", String(20)),
            group='edit')
    comments = deferred(Column("comments", Text),
            group='edit')
    creationDate = deferred(Column("creationDate", CustomDateType,
                                            default=get_current_timestamp))
    updateDate = deferred(Column("updateDate", CustomDateType,
                                        default=get_current_timestamp,
                                        onupdate=get_current_timestamp))
    active = deferred(Column("active", String(1), default="Y"))
    logo = deferred(Column("logo", CustomFileType("logo_", 255)),
            group='edit')
    header = deferred(Column("header", CustomFileType("header_", 255)),
            group='edit')
    logoType = deferred(Column("logoType", String(255)))
    headerType = deferred(Column("headerType", String(255)))
    RIB = deferred(Column("RIB", String(255)),
            group='edit')
    IBAN = deferred(Column("IBAN", String(255)),
            group='edit')
    clients = relationship("Client",
                            order_by="Client.code",
                            backref='company')
    projects = relationship("Project",
                            order_by="Project.id",
                            backref="company")

    def get_path(self):
        """
            get the relative filepath specific to the given company
        """
        return os.path.join("company", str(self.id))

    def get_header_filepath(self):
        """
            Returns the header's relative filepath
        """
        if self.header:
            return os.path.join(self.get_path(),
                            'header',
                            self.header['filename'])
        else:
            return None

    def get_logo_filepath(self):
        """
            Return the logo's relative filepath
        """
        if self.logo:
            return os.path.join(self.get_path(),
                            'logo',
                             self.logo['filename'])
        else:
            return None

    def get_company_id(self):
        """
            Return the current company id
            Allows company id access through request's context
        """
        return self.id

    @classmethod
    def query(cls, keys=None, active=True):
        """
            Return a query
        """
        if keys:
            query = DBSESSION.query(*keys)
        else:
            query = super(Company, cls).query()
        if active:
            query = query.filter(cls.active=="Y")
        return query.order_by(cls.name)

    def disable(self):
        """
            Disable the current company
        """
        self.active = "N"

    def has_invoices(self):
        """
            return True if this company owns invoices
        """
        for project in self.projects:
            for invoice in project.invoices:
                if invoice.has_been_validated():
                    return True
        return False

    def todict(self):
        """
            return a dict representation
        """
        clients = [client.todict() for client in self.clients]
        projects = [project.todict() for project in self.projects]
        return dict(id=self.id,
                    name=self.name,
                    goal=self.goal,
                    email=self.email,
                    phone=self.phone,
                    mobile=self.mobile,
                    comments=self.comments,
                    RIB=self.RIB,
                    IBAN=self.IBAN,
                    logo=self.get_logo_filepath(),
                    header=self.get_header_filepath(),
                    clients=clients,
                    projects=projects)
