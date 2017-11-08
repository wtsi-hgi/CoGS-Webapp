"""
Copyright (c) 2017 Genome Research Ltd.

Authors:
* Simon Beal <sb48@sanger.ac.uk>
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

from sqlalchemy import Integer, String, Column, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


def _base_repr(self):
    """
    Monkeypatch the Base object so it's `eval`able

    :param self:
    :return str:
    """
    params = ", ".join("{}={}".format(column.key, repr(getattr(self, column.key)))
                       for column in self.__table__.columns)

    return f"{self.__class__.__name__}({params})"

Base = declarative_base()
Base.__repr__ = _base_repr


class ProjectGroup(Base):
    __tablename__          = "project_groups"

    id                     = Column(Integer, primary_key=True)
    supervisor_submit      = Column(Date)
    student_invite         = Column(Date)
    student_choice         = Column(Date)
    student_complete       = Column(Date)
    marking_complete       = Column(Date)
    series                 = Column(Integer)
    part                   = Column(Integer)
    student_viewable       = Column(Boolean)
    student_choosable      = Column(Boolean)
    student_uploadable     = Column(Boolean)
    can_finalise           = Column(Boolean)
    read_only              = Column(Boolean)  # Can supervisors modify the projects in this group

    projects               = relationship("Project")


class ProjectGrade(Base):
    __tablename__          = "project_grades"

    id                     = Column(Integer, primary_key=True)
    grade_id               = Column(Integer)
    good_feedback          = Column(String)
    bad_feedback           = Column(String)
    general_feedback       = Column(String)


class Project(Base):
    __tablename__          = "projects"

    id                     = Column(Integer, primary_key=True)
    title                  = Column(String)
    small_info             = Column(String)
    abstract               = Column(String)
    is_computational       = Column(Boolean)
    is_wetlab              = Column(Boolean)
    programmes             = Column(String)

    uploaded               = Column(Boolean)
    grace_passed           = Column(Boolean)

    supervisor_id          = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    cogs_marker_id         = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    student_id             = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    group_id               = Column(Integer, ForeignKey(ProjectGroup.id, ondelete="CASCADE"))

    supervisor_feedback_id = Column(Integer, ForeignKey(ProjectGrade.id, ondelete="CASCADE"))
    cogs_feedback_id       = Column(Integer, ForeignKey(ProjectGrade.id, ondelete="CASCADE"))

    supervisor             = relationship("User",       foreign_keys=supervisor_id, post_update=True)
    cogs_marker            = relationship("User",       foreign_keys=cogs_marker_id, post_update=True)
    student                = relationship("User",       foreign_keys=student_id, post_update=True)
    group                  = relationship(ProjectGroup, foreign_keys=group_id)
    supervisor_feedback    = relationship(ProjectGrade, foreign_keys=supervisor_feedback_id)
    cogs_feedback          = relationship(ProjectGrade, foreign_keys=cogs_feedback_id)


class User(Base):
    __tablename__          = "users"

    id                     = Column(Integer, primary_key=True)
    name                   = Column(String)
    email                  = Column(String)
    user_type              = Column(String)

    priority               = Column(Integer)

    first_option_id        = Column(Integer, ForeignKey(Project.id, ondelete="SET NULL"))
    second_option_id       = Column(Integer, ForeignKey(Project.id, ondelete="SET NULL"))
    third_option_id        = Column(Integer, ForeignKey(Project.id, ondelete="SET NULL"))

    first_option           = relationship(Project, foreign_keys=first_option_id, post_update=True)
    second_option          = relationship(Project, foreign_keys=second_option_id, post_update=True)
    third_option           = relationship(Project, foreign_keys=third_option_id, post_update=True)


class EmailTemplate(Base):
    __tablename__          = "email_templates"

    id                     = Column(Integer, primary_key=True)
    name                   = Column(String)

    subject                = Column(String)
    content                = Column(String)