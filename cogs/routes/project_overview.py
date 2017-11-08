from typing import Dict

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_jinja2 import template

from cogs.db.functions import get_most_recent_group, get_group, get_series, get_user_id, set_group_attributes, get_navbar_data
from permissions import can_view_group, get_user_permissions


@template('group_overview.jinja2')
async def group_overview(request: Request) -> Dict:
    """
    Find the correct group and send it to the user.

    :param request:
    :return Response:
    """
    session = request.app["session"]
    cookies = request.cookies
    most_recent = get_most_recent_group(session)
    user = get_user_id(request.app, request.cookies)
    permissions = get_user_permissions(request.app, user)
    if "group_series" in request.match_info:
        series = int(request.match_info["group_series"])
        part = int(request.match_info["group_part"])
        group = get_group(session, series, part)
    else:
        group = most_recent
    if group is None:
        return web.Response(status=404, text="No projects found")
    elif group is most_recent:
        if not can_view_group(request, group):
            return web.Response(status=403, text="Cannot view rotation")
    return {"project_list": set_group_attributes(request.app, cookies, group),
            "user": user,
            "show_vote": "join_projects" in permissions,
            "cur_option": "projects",
            **get_navbar_data(request)}


@template('group_list_overview.jinja2')
async def series_overview(request: Request) -> Dict:
    """
    Find the correct series as well as all groups in that series.

    :param request:
    :return Response:
    """
    session = request.app["session"]
    cookies = request.cookies
    series = int(request.match_info["group_series"])
    groups = get_series(session, series)
    projects = (set_group_attributes(request.app, cookies, group) for group in groups if can_view_group(request, group))
    return {"series_list": projects,
            "user": get_user_id(request.app, request.cookies),
            "cur_option": "projects",
            **get_navbar_data(request)}
