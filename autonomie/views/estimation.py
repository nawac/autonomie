# -*- coding: utf-8 -*-
# * File Name : estimation.py
#
# * Copyright (C) 2010 Gaston TJEBBES <g.t@majerti.fr>
# * Company : Majerti ( http://www.majerti.fr )
#
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 24-04-2012
# * Last Modified :
#
# * Project :
#
"""
    Estimation views
"""
import logging
from deform import ValidationFailure
from deform import Form
from pyramid.view import view_config
from autonomie.models import DBSESSION
from autonomie.models.model import Tva
from autonomie.models.model import Estimation
from autonomie.views.forms.estimation import EstimationSchema
from autonomie.views.forms.estimation import get_appstruct
from autonomie.views.forms.estimation import get_dbdatas

log = logging.getLogger(__name__)
def get_tvas():
    """
        return all configured tva amounts
    """
    tvas = DBSESSION().query(Tva).all()
    return [(tva.value, tva.name)for tva in tvas]


@view_config(route_name="estimations", renderer='estimation.mako')
@view_config(route_name='estimation', renderer='estimation.mako')
def estimation_form(request):
    """
        Return the estimation edit view
    """
    log.debug("In estimation view")
    cid = request.matchdict.get('cid')
    project_id = request.matchdict.get('id')
    avatar = request.session['user']

    company = avatar.get_company(cid)
    project = company.get_project(project_id)

    taskid = request.matchdict.get('taskid')
    log.debug("We've got a task : {0}".format(taskid))
    if taskid:
        estimation = project.get_estimation(taskid)
        estimation_lines = estimation.lines
        payment_lines = estimation.payment_lines
        title = u"Édition du devis"
    else:
        phaseid = request.params.get('phase')
        estimation = Estimation()
        estimation.IDPhase = phaseid
        estimation_lines = []
        payment_lines = []
        title = u"Nouveau devis"
    dbdatas = {'estimation':estimation.appstruct(),
               'estimation_lines':[line.appstruct()
                                    for line in estimation_lines],
               'payment_lines':[line.appstruct()
                                    for line in payment_lines]}
    log.debug("DBDatas :")
    log.debug(dbdatas)
    appstruct = get_appstruct(dbdatas)
    log.debug(appstruct)

    phase_choices = ((phase.id, phase.name) for phase in project.phases)
    schema = EstimationSchema().bind(phases=phase_choices,
                                     tvas=get_tvas())
    form = Form(schema, buttons=("submit", ))


    if 'submit' in request.params:
        log.debug('***** Submitted')
        datas = request.params.items()
        log.debug(datas)
        try:
            appstruct = form.validate(datas)
            log.debug("   + Validated : appstruct")
            log.debug(appstruct)
        except ValidationFailure, e:
            log.debug("   - Error in validation")
            html_form = e.render()
        else:
            dbdatas = get_dbdatas(appstruct)
            log.debug("DB DATAS : ")
            log.debug(dbdatas)
            html_form = form.render(appstruct)
    else:
        html_form = form.render(appstruct)
    return dict(title=title,
                client=project.client,
                company=company,
                html_form = html_form
                )
