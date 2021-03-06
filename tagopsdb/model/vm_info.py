# Copyright 2016 Ifwe Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from .meta import Base, Column, String


class VmInfo(Base):
    __tablename__ = 'vm_info'

    host_id = Column(
        u'host_id',
        INTEGER(),
        ForeignKey(
            'hosts.HostID',
            name='fk_vm_info_host_id_hosts',
            ondelete='cascade'
        ),
        primary_key=True
    )
    pool = Column(String(length=10), nullable=False)
    numa_mode = Column(INTEGER(), server_default=None)

    host = relationship('Host', uselist=False, back_populates='vm')
