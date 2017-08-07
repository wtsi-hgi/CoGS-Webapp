from sqlalchemy import create_engine, Integer, String, Column, Date, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


def base_repr(self):
    """
    Monkeypatch the Base object so it's `eval`able
    :param self:
    :return str:
    """
    params = ", ".join("{}={}".format(column.key, repr(getattr(self, column.key)))
                       for column in self.__table__.columns)
    return f"{self.__class__.__name__}({params})"


Base = declarative_base()
Base.__repr__ = base_repr


class ProjectGroup(Base):
    __tablename__ = "project_group"
    id = Column(Integer, primary_key=True)
    supervisor_submit = Column(Date)
    grad_office_review = Column(Date)
    student_invite = Column(Date)
    student_choice = Column(Date)
    student_complete = Column(Date)
    marking_complete = Column(Date)
    series = Column(Integer)
    part = Column(Integer)
    student_choosable = Column(Boolean)
    student_viewable = Column(Boolean)
    read_only = Column(Boolean)

    projects = relationship("Project")


class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    abstract = Column(String)
    supervisor_id = Column(Integer, ForeignKey("user.id"))
    cogs_marker_id = Column(Integer, ForeignKey("user.id"))
    student_id = Column(Integer, ForeignKey("user.id"))
    group_id = Column(Integer, ForeignKey(ProjectGroup.id))
    is_computational = Column(Boolean)
    is_wetlab = Column(Boolean)

    supervisor = relationship("User", foreign_keys=supervisor_id)
    cogs_marker = relationship("User", foreign_keys=cogs_marker_id)
    student = relationship("User", foreign_keys=student_id)
    group = relationship(ProjectGroup, foreign_keys=group_id)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    #first_option_id = Column(Integer, ForeignKey(Project.id))
    #second_option_id = Column(Integer, ForeignKey(Project.id))
    name = Column(String)

    #first_option = relationship(Project, foreign_keys=first_option_id, primaryjoin=first_option_id == Project.id, post_update=True)
    #second_option = relationship(Project, foreign_keys=second_option_id, primaryjoin=second_option_id == Project.id, post_update=True)


async def init_pg(app):
    """
    Initialise the database and connect it to the app
    Also adds debugging structures to the database
    :param app:
    :return session:
    """
    conf = app["db_config"]
    engine = create_engine(f"postgresql://{conf['user']}@{conf['host']}/{conf['name']}")
    # TODO: DELETEME
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    app["db"] = engine

    Session = sessionmaker(bind=engine)
    app["session"] = session = Session()

    # TODO: DELETEME
    test_user = User(name="A supervisor")
    session.add(test_user)
    for username in ["Alpha", "Beta", "Gamma", "Zeta"]:
        session.add(User(name=username))
    test_group = ProjectGroup(series=2017,
                              part=3,
                              supervisor_submit=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                              grad_office_review=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                              student_invite=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                              student_choice=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                              student_complete=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                              marking_complete=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                              student_viewable=True,
                              student_choosable=True,
                              read_only=False)
    test_group_2 = ProjectGroup(series=2017,
                                part=1,
                                supervisor_submit=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                                grad_office_review=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                                student_invite=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                                student_choice=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                                student_complete=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                                marking_complete=datetime.strptime("01/01/2017", "%d/%m/%Y"),
                                student_viewable=True,
                                student_choosable=True,
                                read_only=True)
    session.add(test_group_2)
    session.add(test_group)
    session.flush()
    session.add(Project(title="Studying the effects of using Lorem Ipsum text",
                        abstract="",
                        supervisor_id=test_user.id,
                        group_id=test_group_2.id,
                        is_computational=False,
                        is_wetlab=True))
    session.add(Project(title="Doing things with another thing",
                        abstract="Stuff happened",
                        supervisor_id=test_user.id,
                        group_id=test_group.id,
                        is_computational=True,
                        is_wetlab=True))
    session.add(Project(title="Improving performance with thing",
                        abstract="It's fun",
                        supervisor_id=test_user.id,
                        group_id=test_group.id,
                        is_computational=True,
                        is_wetlab=False))
    session.flush()
    return session


async def close_pg(app):
    """
    Clean up the database at shutdown.

    :param app:
    :return:
    """
    app["session"].close()
