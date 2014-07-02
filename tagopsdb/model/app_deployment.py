from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT, TIMESTAMP
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func, select

from .meta import Base, Column, String
from .environment import Environment

class AppDeployment(Base):
    __tablename__ = 'app_deployments'

    id = Column(u'AppDeploymentID', INTEGER(), primary_key=True)
    deployment_id = Column(
        u'DeploymentID',
        INTEGER(),
        ForeignKey('deployments.DeploymentID', ondelete='cascade'),
        nullable=False
    )
    app_id = Column(
        u'AppID',
        SMALLINT(display_width=6),
        ForeignKey('app_definitions.AppID', ondelete='cascade'),
        nullable=False
    )
    user = Column(String(length=32), nullable=False)
    status = Column(
        Enum(
            'complete',
            'incomplete',
            'inprogress',
            'invalidated',
            'validated',
        ),
        nullable=False
    )
    environment_id = Column(
        u'environment_id',
        INTEGER(),
        ForeignKey('environments.environmentID', ondelete='cascade'),
        nullable=False
    )
    realized = Column(
        TIMESTAMP(),
        nullable=False,
        server_default=func.current_timestamp()
    )
    environment_obj = relationship('Environment')

    @hybrid_property
    def environment(self):
        return self.environment_obj.environment

    @environment.expression
    def environment(cls):
        return select([Environment.environment]).\
                where(Environment.id == cls.environment_id).correlate(cls).\
                label('environment')