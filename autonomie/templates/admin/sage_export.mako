<%doc>
 * Copyright (C) 2012-2013 Croissance Commune
 * Authors:
       * Arezki Feth <f.a@majerti.fr>;
       * Miotte Julien <j.m@majerti.fr>;
       * Pettier Gabriel;
       * TJEBBES Gaston <g.t@majerti.fr>

 This file is part of Autonomie : Progiciel de gestion de CAE.

    Autonomie is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Autonomie is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Autonomie.  If not, see <http://www.gnu.org/licenses/>.
</%doc>

<%inherit file="/admin/index.mako"></%inherit>
<%block name='content'>
% if check_messages is not None:
    <div class='row-fluid'>
        <div class='span6 offset3'>
            <h2>${check_messages['title']}</h2>
        </div>
    </div>
    <p class='text-error'>
    % for message in check_messages['errors']:
        <b>*</b> ${message|n}<br />
    % endfor
    </p>
% endif
% for form in (all_form, period_form, from_invoice_number_form, invoice_number_form):
    <div class='row-fluid'>
    <div class='span6 offset3'>
        ${form|n}
    </div>
</div>
% endfor
</%block>
