#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# /omd/sites/lab/local/lib/python3/cmk/gui/plugins/views/better_tiles.py

from collections.abc import Sequence

from cmk.gui.htmllib.html import html
from cmk.gui.i18n import _
from cmk.gui.logged_in import user
from cmk.gui.painter.v0.base import Cell, EmptyCell
from cmk.gui.table import init_rowselect
from cmk.gui.type_defs import Rows, ViewSpec
from cmk.gui.visual_link import render_link_to_view


from cmk.gui.views.layout import layout_registry
from cmk.gui.views.layout.helpers import group_value
from cmk.gui.views.layout.layouts import LayoutTiled, _get_view_name


class LayoutBetterTiles(LayoutTiled):
    """An improved version of the tiled layout with rounded corners, larger text,
    and the entire tile is clickable."""

    @property
    def ident(self) -> str:
        return "better_tiles"

    @property
    def title(self) -> str:
        return _("Better Tiles")

    def render(
        self,
        rows: Rows,
        view: ViewSpec,
        group_cells: Sequence[Cell],
        cells: Sequence[Cell],
        num_columns: int,
        show_checkboxes: bool,
    ) -> None:
        html.open_table(class_="data tiled better_tiles")

        last_group = None
        group_open = False
        for row in rows:
            # Show group header
            if group_cells:
                this_group = group_value(row, group_cells)
                if this_group != last_group:
                    # paint group header
                    if group_open:
                        html.close_td()
                        html.close_tr()
                    html.open_tr()
                    html.open_td()
                    html.open_table(class_="groupheader")
                    html.open_tr(class_="groupheader")

                    painted = False
                    for cell in group_cells:
                        if painted:
                            html.td(",&nbsp;")
                        painted = cell.paint(row, render_link_to_view)

                    html.close_tr()
                    html.close_table()

                    html.close_td()
                    html.close_tr()

                    html.open_tr()
                    html.open_td(class_="tiles")

                    group_open = True
                    last_group = this_group

            # background color of tile according to item state
            state = row.get("service_state", -1)
            if state == -1:
                hbc = row.get("host_has_been_checked", 1)
                if hbc:
                    state = row.get("host_state", 0)
                    sclass = "hhstate%d" % state
                else:
                    sclass = "hhstatep"
            else:
                hbc = row.get("service_has_been_checked", 1)
                if hbc:
                    sclass = "sstate%d" % state
                else:
                    sclass = "sstatep"

            if not group_open:
                html.open_tr()
                html.open_td(class_="tiles")
                group_open = True

            # Get the link URL for the entire tile
            link_url = None
            for cell in cells:
                if hasattr(cell, "url") and cell.url:
                    link_url = cell.url(row)
                    break

            # Make the entire div clickable by wrapping it in an <a> tag
            if link_url:
                html.open_a(href=link_url, class_="tile_link")

            html.open_div(class_=["tile", "better_tile", sclass])
            html.open_table()

            # We need at least five cells
            render_cells = list(cells)
            if len(render_cells) < 5:
                render_cells += [EmptyCell(None, None)] * (5 - len(render_cells))

            rendered = [cell.render(row, render_link_to_view) for cell in render_cells]

            html.open_tr()
            html.open_td(colspan=2, class_=["center", "larger_text", rendered[0][0]])
            html.write_text(rendered[0][1])
            html.close_td()
            html.close_tr()

            for css, cont in rendered[5:]:
                html.open_tr()
                html.open_td(colspan=2, class_=["cont", css])
                html.write_text(cont)
                html.close_td()
                html.close_tr()

            html.close_table()
            html.close_div()

            if link_url:
                html.close_a()

        if group_open:
            html.close_td()
            html.close_tr()

        html.close_table()

        # Add custom CSS for better tiles
        html.style("""
        .better_tiles .better_tile {
            border-radius: 8px;
            transition: transform 0.2s ease;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .better_tiles .better_tile td.center {
            border-radius: 6px;
        }

        .better_tiles .better_tile:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .better_tiles .larger_text {
            font-size: 120%;
            font-weight: bold;
        }

        .better_tiles a.tile_link {
            text-decoration: none;
            color: inherit;
            display: block;
            width: 100%;
            height: 100%;
        }

        .better_tiles .tile_link:focus {
            outline: none;
        }

        .better_tiles .better_tile table {
            height: 50px !important;
            width: 100%;
        }
        """)

        if not user.may("general.act"):
            return

        init_rowselect(_get_view_name(view))

layout_registry.register(LayoutBetterTiles)