# -*- coding: utf-8 -*-
# * File Name : __init__.py
#
# * Copyright (C) 2012 Majerti <tech@majerti.fr>
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 11-01-2012
# * Last Modified : dim. 12 sept. 2010 06:56:51 CEST
#
# * Project : autonomie
#
"""
    Main file for our pyramid application
"""
import locale
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid_beaker import set_cache_regions_from_settings
from sqlalchemy import engine_from_config

from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from autonomie.utils.security import RootFactory
from autonomie.utils.security import BaseDBFactory
from autonomie.utils.security import wrap_db_objects

from autonomie.models.initialize import initialize_sql
from autonomie.models.config import get_config
from autonomie.utils.avatar import get_groups
from autonomie.utils.avatar import get_avatar
from autonomie.utils.renderer import set_deform_renderer


def main(global_config, **settings):
    """
        Main function : returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings)
    auth_policy = SessionAuthenticationPolicy(callback=get_groups)
    acl_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,
                        authentication_policy=auth_policy,
                        authorization_policy=acl_policy,
                        session_factory=session_factory)
    config.begin()
    config.commit()

    dbsession = initialize_sql(engine)
    wrap_db_objects()
    BaseDBFactory.dbsession = dbsession
    config._set_root_factory(RootFactory)

    # Application main configuration
    config.set_default_permission('view')

    # Adding some properties to the request object
    config.set_request_property(lambda _: dbsession(), 'dbsession', reify=True)
    config.set_request_property(get_avatar, 'user', reify=True)
    config.set_request_property(lambda _:get_config(), 'config')

    config.add_static_view('static', 'autonomie:static', cache_max_age=3600)
    config.add_static_view('deformstatic', "deform:static", cache_max_age=3600)

    # Adding a static view to the configured assets
    config.add_static_view('assets', settings.get('autonomie.assets',
                                                  '/var/intranet_files'),
                                                          cache_max_age=3600)

    # Common routes
    config.add_route('index', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('account',
                    '/account')

    # Holiday routes
    config.add_route('holiday',  # Add
                    '/holiday')
    config.add_route('holidays',  # view
                    '/holidays')

    config.add_route('statistic',
                    '/statistics/{id:\d+}',
                    traverse='/companies/{id}')
    config.add_route('statistics',  # view
                    '/statistics')
    # Company Handling
    config.include("autonomie.views.company")
    # * Projects
    config.include("autonomie.views.project")
    # Customer handling
    config.include("autonomie.views.client")
    # * Invoices
    config.add_route('company_invoices',
                     '/company/{id:\d+}/invoices',
                     traverse='/companies/{id}')
    # * Treasury
    config.add_route('company_treasury',
                     '/company/{id:\d+}/treasury',
                     traverse='/companies/{id}')

    #Tasks (estimation and invoice) routes
    config.add_route('estimations',
                     '/projects/{id:\d+}/estimations',
                      traverse='/projects/{id}')
    config.add_route('estimation',
                     '/estimations/{id:\d+}',
                      traverse='/estimations/{id}')

    config.add_route('project_invoices',
                     '/projects/{id:\d+}/invoices',
                     traverse='/projects/{id}')
    config.add_route('invoice',
                     '/invoices/{id:\d+}',
                     traverse='/invoices/{id}')

    config.add_route("invoices",
                    "/invoices")

    config.add_route("cancelinvoices",
                     "/projects/{id:\d+}/cancelinvoices",
                     traverse='/projects/{id}')
    config.add_route("cancelinvoice",
                    "/cancelinvoices/{id:\d+}",
                    traverse='/cancelinvoices/{id}')

    config.include("autonomie.views.admin")
    config.include("autonomie.views.user")

    # Manage main view
    config.include("autonomie.views.manage")

    # Test javascript view
    config.add_route("testjs",
                    "/testjs")
    # Set deform multi renderer handling translation and both chameleon and
    # mako templates
    set_deform_renderer()
    config.scan('autonomie.views')
    config.add_translation_dirs("colander:locale/", "deform:locale")
    locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

    return config.make_wsgi_app()
