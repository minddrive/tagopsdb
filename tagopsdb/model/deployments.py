from elixir import Field
from elixir import String, Integer, Enum, DateTime
from elixir import using_options, belongs_to, has_many
from sqlalchemy.sql.expression import func

from .base import Base


class Deployments(Base):
    using_options(tablename='deployments')

    id = Field(Integer, colname='DeploymentID', primary_key=True)
    user = Field(String(length=32), required=True)
    dep_type = Field(
        Enum('deploy', 'rollback'),
        required=True,
    )

    declared = Field(
        DateTime,
        required=True,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )

    belongs_to(
        'package',
        of_kind='Packages',
        colname='package_id',
        target_column='package_id',
        ondelete='cascade',
        required=True,
        inverse='deployments'
    )

    has_many(
        'app_deployments',
        of_kind='AppDeployments',
        inverse='deployment',
    )

    has_many(
        'host_deployments',
        of_kind='HostDeployments',
        inverse='deployment',
    )