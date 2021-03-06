"""
Copyright (c) 2017 Genome Research Ltd.

Authors:
* Christopher Harrison <ch12@sanger.ac.uk>

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

# TODO: there is no good reason for the available roles to be
# dynamically generated from a config file rather than just being
# hard-coded. All this does is make the code harder to read and
# impossible to type-check.

import textwrap
from typing import Any, Dict, Type, TYPE_CHECKING

from cogs.common.constants import PERMISSIONS


class _BaseRole(object):
    """Base role object.

    NOTE Do not instantiate!
    """
    _permissions: Dict[str, bool]

    def __init__(self, **permissions: bool) -> None:
        self._permissions = permissions

    def __repr__(self):
        params = ", ".join("{}={}".format(k, repr(v)) for k, v in self._permissions.items())
        return f"{self.__class__.__name__}({params})"

    def __bool__(self):
        return any(self._permissions.values())

    def __eq__(self, other: object) -> bool:
        """ Role equivalence """
        if not isinstance(other, _BaseRole):
            return NotImplemented
        return self.__class__ == other.__class__ \
           and all(v == other._permissions[k]
                   for k, v in self._permissions.items())

    def __or__(self, other: "_BaseRole") -> "_BaseRole":
        """ Logical disjunction of equivalent permissions """
        assert self.__class__ == other.__class__
        return self.__class__(**{k: v | other._permissions[k]
                                 for k, v in self._permissions.items()})

    def __and__(self, other: "_BaseRole") -> "_BaseRole":
        """ Logical conjunction of equivalent permissions """
        assert self.__class__ == other.__class__
        return self.__class__(**{k: v & other._permissions[k]
                                 for k, v in self._permissions.items()})

    def serialise(self):
        return self._permissions


def _build_role(*permissions: str) -> Type[_BaseRole]:
    """
    Build a role class with a constructor taking boolean arguments
    matching the specified permissions, with respective, read-only
    properties

    This uses the same kind of ugly metaprogramming as the standard
    library uses to build namedtuples... Approach with caution!
    """
    assert permissions  # Must have at least one

    # Define constructor
    src = """
    class Role(_BaseRole):
        def __init__(self, *, {init_params}) -> None:
            super().__init__(**{{ {param_dict} }})
    """.format(
        init_params = ", ".join(map(lambda p: f"{p}:bool", permissions)),
        param_dict  = ", ".join(map(lambda p: f"\"{p}\": {p}", permissions))
    )

    # Define properties
    for p in permissions:
        src += """
        @property
        def {p}(self) -> bool:
            return self._permissions["{p}"]
        """.format(p=p)

    # Oh god, now I'm going to need to take a shower :P
    namespace = {"_BaseRole": _BaseRole}
    exec(textwrap.dedent(src), namespace)
    return namespace["Role"]


# Role is fundamentally impossible to typecheck, unfortunately; this
# avoids mypy telling us that Role is "not valid as a type".
if TYPE_CHECKING:
    Role = Any
else:
    Role = _build_role(*PERMISSIONS)
