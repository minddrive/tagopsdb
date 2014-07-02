import sqlalchemy

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import object_mapper, scoped_session, sessionmaker

from .schema import References


def init(**config):
    url = config.pop('url', {})
    url.setdefault('drivername', 'mysql+oursql')
    url.setdefault('database', 'TagOpsDB')
    do_create = config.pop('create', False)

    if do_create:
        create_url = url.copy()
        db_name = create_url.pop('database')
        engine = sqlalchemy.create_engine(URL(**create_url), **config)
        engine.execute('CREATE DATABASE IF NOT EXISTS %s' % db_name)

    engine = sqlalchemy.create_engine(
        URL(**url), **config
    )
    Base.metadata.bind = engine

    if do_create:
        Base.metadata.create_all(engine)

    Session.configure(bind=engine)


def destroy():
    Session.close()
    sqlalchemy.orm.clear_mappers()
    Base.metadata.drop_all()
    Base.metadata.bind.execute('DROP DATABASE IF EXISTS %s' % Base.metadata.bind.url.database)
    Base.metadata.clear()


class TagOpsDB(References):
    """Base class for some common default settings"""

    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'},
    )

    def __repr__(self):
        mapper = object_mapper(self)
        keyvals = [(key, getattr(self, key))
                   for key in mapper.columns.keys()]

        return '<%(class_name)s (%(table_name)s) %(keyvals_string)s>' % dict(
            class_name = type(self).__name__,
            table_name = self.__table__.name,
            keyvals_string =
                ' '.join('%s=%r'% (key, val) for (key, val) in keyvals),
        )

    def delete(self, *args, **kwargs):
        return Session.delete(self, *args, **kwargs)

    @classmethod
    def query(cls):
        return Session.query(cls)

    @classmethod
    def get_by(cls, **kwds):
        try:
            return cls.query().filter_by(**kwds).one()
        except sqlalchemy.orm.exc.NoResultFound as e:
            return None

    get = get_by

    @classmethod
    def all(cls, *args, **kwargs):
        q = cls.query()
        if 'limit' in kwargs:
            q = q.limit(kwargs.pop('limit'))

        return q.all(*args, **kwargs)

    @classmethod
    def update_or_create(cls, data, surrogate=True):
        pk_props = [x for x in cls.__table__.columns if x.primary_key]

        # if all pk are present and not None
        if not [1 for p in pk_props if data.get(p.key) is None]:
            pk_tuple = tuple([data[prop.key] for prop in pk_props])
            record = cls.query().get(pk_tuple)
            if record is None:
                if surrogate:
                    raise Exception("Cannot create surrogate with pk")
                else:
                    record = cls()
        else:
            if surrogate:
                record = cls()
            else:
                raise Exception("Cannot create non surrogate without pk")
        record.from_dict(data)
        Session.add(record)
        return record

    @classmethod
    def first(cls, *args, **kwargs):
        return cls.query().first(*args, **kwargs)

    def from_dict(self, data):
        """
        Update a mapped class with data from a JSON-style nested dict/list
        structure.
        """
        # surrogate can be guessed from autoincrement/sequence but I guess
        # that's not 100% reliable, so we'll need an override

        mapper = sqlalchemy.orm.object_mapper(self)

        for key, value in data.iteritems():
            if isinstance(value, dict):
                dbvalue = getattr(self, key)
                rel_class = mapper.get_property(key).mapper.class_
                pk_props = rel_class._descriptor.primary_key_properties

                # If the data doesn't contain any pk, and the relationship
                # already has a value, update that record.
                if not [1 for p in pk_props if p.key in data] and \
                   dbvalue is not None:
                    dbvalue.from_dict(value)
                else:
                    record = rel_class.update_or_create(value)
                    setattr(self, key, record)
            elif isinstance(value, list) and \
                 value and isinstance(value[0], dict):

                rel_class = mapper.get_property(key).mapper.class_
                new_attr_value = []
                for row in value:
                    if not isinstance(row, dict):
                        raise Exception(
                                'Cannot send mixed (dict/non dict) data '
                                'to list relationships in from_dict data.')
                    record = rel_class.update_or_create(row)
                    new_attr_value.append(record)
                setattr(self, key, new_attr_value)
            else:
                setattr(self, key, value)


Session = scoped_session(sessionmaker())

Base = declarative_base(cls=TagOpsDB)

# Constraint naming convention
#Base.metadata.naming_convention = {
#    "ix": 'ix_%(table_name)s_%(column_0_name)s',
#    "uq": "uq_%(table_name)s_%(column_0_name)s",
#    "ck": "ck_%(table_name)s_%(constraint_name)s",
#    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#    "pk": "pk_%(table_name)s",
#}