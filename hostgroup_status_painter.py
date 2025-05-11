#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.painter.v0.base import Painter, painter_registry
from cmk.gui.type_defs import Row
import cmk.gui.sites as sites
from cmk.gui.i18n import _
from cmk.gui.htmllib.html import html


class PainterHostGroupStatusAlias(Painter):
    @property
    def ident(self) -> str:
        return "hostgroup_status_alias"
    
    def title(self, cell) -> str:
        return _("Host Group: Alias with status color (excluding acknowledged)")
    
    def short_title(self, cell) -> str:
        return _("Group Status")
    
    @property
    def columns(self) -> list[str]:
        return [
            "hostgroup_name", 
            "hostgroup_alias",
            "hostgroup_num_services_ok",
            "hostgroup_num_services_warn",
            "hostgroup_num_services_crit",
            "hostgroup_num_services_unknown",
            "hostgroup_num_services_pending"
        ]
    
    def render(self, row: Row, cell) -> tuple[str, str]:
        hostgroup_name = row.get("hostgroup_name", "")
        hostgroup_alias = row.get("hostgroup_alias", hostgroup_name)
        
        if not hostgroup_name:
            return "", ""
        
        # Query live status to get all services for hosts in this group
        # Include acknowledged state and filter out acknowledged services
        query = """GET services
Columns: state host_name description acknowledged
Filter: host_groups >= %s
Filter: acknowledged = 0
""" % hostgroup_name
        
        try:
            data = sites.live().query_table(query)
            # data will be a list of [state, host_name, description, acknowledged] for each service
            
            # Find the worst state (0=OK, 1=WARN, 2=CRIT, 3=UNKNOWN)
            # Only consider services that are not acknowledged
            worst_state = 0
            for state, _host, _desc, _ack in data:
                if state > worst_state:
                    worst_state = state
                if worst_state == 2:  # No need to check further if we already found CRITICAL
                    break
            
            # Use the exact CSS class format used by built-in painters
            css_class = f"count svcstate state{worst_state}"
            
            # Create the content with the proper HTML structure
            content = html.render_span(hostgroup_alias)
            
            return css_class, content
        
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger("cmk.web")
            logger.error(f"Error in HostGroupStatusPainter: {e}")
            
            # Just return the alias without color in case of error
            return "", hostgroup_alias


# Register the painter
painter_registry.register(PainterHostGroupStatusAlias)
