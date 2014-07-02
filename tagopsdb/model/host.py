from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import select

from .meta import Base, Column, String
from .environment import Environment


class Host(Base):
    __tablename__ = 'hosts'

    id = Column(u'HostID', INTEGER(), primary_key=True)
    spec_id = Column(u'SpecID', INTEGER(), ForeignKey('host_specs.specID'))
    state = Column(
        Enum(
            u'baremetal',
            u'operational',
            u'repair',
            u'parts',
            u'reserved',
            u'escrow'
        ),
        nullable=False
    )
    hostname = Column(String(length=30))
    arch = Column(String(length=10))
    kernel_version = Column(u'kernelVersion', String(length=20))
    distribution = Column(String(length=20))
    timezone = Column(String(length=10))
    app_id = Column(
        u'AppID',
        SMALLINT(display_width=6),
        ForeignKey('app_definitions.AppID'),
        nullable=False
    )
    cage_location = Column(u'cageLocation', INTEGER())
    cab_location = Column(u'cabLocation', String(length=10))
    section = Column(String(length=10))
    rack_location = Column(u'rackLocation', INTEGER())
    console_port = Column(u'consolePort', String(length=11))
    power_port = Column(u'powerPort', String(length=10))
    power_circuit = Column(u'powerCircuit', String(length=10))
    environment_id = Column(
        u'environment_id',
        INTEGER(),
        ForeignKey('environments.environmentID', ondelete='cascade'),
        server_default=None
    )
    environment_obj = relationship('Environment')
    host_deployments = relationship('HostDeployment')
    host_interfaces = relationship('HostInterface', backref='host')
    host_spec = relationship('HostSpec', uselist=False, backref='hosts')
    ilom = relationship('Ilom', uselist=False, backref='host')
    service_events = relationship('ServiceEvent', backref='host')

    @hybrid_property
    def environment(self):
        return getattr(self.environment_obj, 'environment', None)

    @environment.expression
    def environment(cls):
        return select([Environment.environment]).\
                where(Environment.id == cls.environment_id).correlate(cls).\
                label('environment')

    __table_args__ = (
        UniqueConstraint(u'cageLocation', u'cabLocation', u'consolePort'),
        UniqueConstraint(u'cageLocation', u'cabLocation', u'rackLocation'),
        { 'mysql_engine' : 'InnoDB', 'mysql_charset' : 'utf8', },
    )