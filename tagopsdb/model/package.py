from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.mysql import INTEGER, TIMESTAMP
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.sql.expression import func

from .meta import Base, Column, String


class Package(Base):
    __tablename__ = 'packages'

    id = Column(u'package_id', INTEGER(), primary_key=True)
    pkg_def_id = Column(
        INTEGER(),
        ForeignKey('package_definitions.pkg_def_id', ondelete='cascade'),
        nullable=False
    )
    pkg_name = Column(String(length=255), nullable=False)
    name = synonym('pkg_name')
    version = Column(String(length=63), nullable=False)
    revision = Column(String(length=63), nullable=False)
    status = Column(
        Enum('completed', 'failed', 'pending', 'processing', 'removed'),
        nullable=False
    )
    created = Column(
        TIMESTAMP(),
        nullable=False,
        server_default=func.current_timestamp()
    )
    creator = Column(String(length=255), nullable=False)
    builder = Column(
        Enum(u'developer', u'hudson', u'jenkins'),
        nullable=False,
        server_default='developer'
    )
    project_type = Column(
        Enum(u'application', u'kafka-config', u'tagconfig'),
        nullable=False,
        server_default='application'
    )
    package_definition = relationship(
        'PackageDefinition',
        back_populates='packages'
    )
    deployments = relationship('Deployment', back_populates='package')

    __table_args__ = (
        UniqueConstraint(u'pkg_name', u'version', u'revision', u'builder',
                         name=u'unique_package'),
        { 'mysql_engine' : 'InnoDB', 'mysql_charset' : 'utf8', },
    )
