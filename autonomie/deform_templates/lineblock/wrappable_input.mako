# -*- coding: utf-8 -*-
<%doc>
    input for estimation/invoice discount
</%doc>
<input class='input-mini' type='text' name="${field.name}" value="${cstruct}" ></input>
<script type="text/javascript">
    deform.addCallback(
        "${field.oid}",
        function (oid) {
            $('#' + oid + " input").blur(function(){
                $(Facade).trigger("totalchange");
            }
        )});
</script>
