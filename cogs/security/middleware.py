"""
Copyright (c) 2017 Genome Research Ltd.

Authors:
* Christopher Harrison <ch12@sanger.ac.uk>
* Simon Beal <sb48@sanger.ac.uk>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from functools import wraps
from typing import Any, Callable

from aiohttp.web import HTTPForbidden, Request, Response

from cogs.common.constants import PERMISSIONS
from cogs.common.types import Handler
from .roles import zero


def permit(*permissions:str) -> Handler:
    """
    Factory that returns a decorator that forbids access to route
    handlers if the authenticated user doesn't have any of the specified
    permissions

    NOTE While it works in a similar way, this should be used as a
    decorator, rather than web application middleware

    :param permissions:
    :return:
    """
    # We must have at least one permission and our given permissions
    # must be a subset of the valid permissions
    assert permissions
    assert set(permissions) <= set(PERMISSIONS)

    def decorator(fn:Handler) -> Handler:
        @wraps(fn)
        async def decorated(request:Request) -> Response:
            """
            Check authenticated user has the necessary permissions

            :param request:
            :return:
            """
            user = request.get("user")
            role = user.role if user else zero

            if not all(getattr(role, p) for p in permissions):
                raise HTTPForbidden(text="Permission denied")

            return await fn(request)

        return decorated

    return decorator


def permit_when_set(column:str, predicate:Callable[[Any], bool] = bool, response:str = "Permission denied") -> Handler:
    """
    Factory that returns a decorator that forbids the setting of the
    most recent group's data (by column) based on the supplied predicate

    NOTE While it works in a similar way, this should be used as a
    decorator, rather than web application middleware

    FIXME This seems...baroque

    :param column:
    :param predicate:
    :param response:
    :return:
    """
    def decorator(fn:Handler) -> Handler:
        @wraps(fn)
        async def decorated(request:Request) -> Response:
            """
            Check predicate against given conditions

            :param request:
            :return:
            """
            db = request.app["db"]
            group = db.get_most_recent_group()

            if not predicate(getattr(group, column)):
                raise HTTPForbidden(text=response)

            return await fn(request)

        return decorated

    return decorator
