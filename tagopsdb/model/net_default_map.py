from elixir import Field
from elixir import String, Integer
from elixir import using_options, belongs_to, using_table_options
from sqlalchemy import UniqueConstraint

from .base import Base


class NetDefaultMap(Base):
    using_options(tablename='net_default_maps')
    using_table_options(
        UniqueConstraint(
            'environment_id',
            'app_id',
            'interface_name',
            name='map_key'
        ),
    )

    id = Field(Integer, colname='net_default_id', primary_key=True)
    interface_name = Field(String(length=10), required=True)

    belongs_to(
        'environment',
        of_kind='Environment',
        colname='environment_id',
        target_column='environmentID',
        required=True,
        ondelete='cascade'
    )

    belongs_to(
        'app',
        of_kind='Application',
        colname='app_id',
        target_column='AppID',
        required=True,
        ondelete='cascade'
    )
