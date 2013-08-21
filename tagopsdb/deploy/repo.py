import sqlalchemy.orm.exc

from tagopsdb.database.meta import Session
from tagopsdb.database.model import AppDefinitions, PackageLocations
from tagopsdb.exceptions import RepoException


def add_app_location(project_type, pkg_type, pkg_name, app_name, path, arch,
                     build_host, environment):
    """Add the location of a given application"""

    # Ensure the environment parameter is boolean
    if environment:
        environment = True
    else:
        environment = False

    project = PackageLocations(project_type, pkg_type, pkg_name, app_name,
                               path, arch, build_host, environment)
    Session.add(project)
    Session.flush()   # Needed to get pkgLocationID generated

    return project


def add_app_packages_mapping(project, app_types):
    """Add the mappings of the app types for a given project"""

    for app_type in app_types:
        try:
            app_def = (Session.query(AppDefinitions)
                              .filter_by(appType=app_type)
                              .one())
        except sqlalchemy.orm.exc.NoResultFound:
            raise RepoException('App type "%s" is not found in the '
                                'AppDefinitions table' % app_type)

        project.app_definitions.append(app_def)


def delete_app_location(app_name):
    """Delete the location of a given application"""

    try:
        app = find_app_location(app_name)
    except sqlalchemy.orm.exc.NoResultFound:
        raise RepoException('No application "%s" to remove from '
                            'PackageLocations table' % app_name)

    Session.delete(app)


def delete_app_packages_mapping(project, app_types):
    """Delete the mappings of the app types for a given project"""

    for app_type in app_types:
        try:
            app_def = (Session.query(AppDefinitions)
                              .filter_by(appType=app_type)
                              .one())
        except sqlalchemy.orm.exc.NoResultFound:
            raise RepoException('App type "%s" is not found in the '
                                'AppDefinitions table' % app_type)

        project.app_definitions.remove(app_def)


def find_app_location(app_name):
    """Find a given project"""

    try:
        return (Session.query(PackageLocations)
                       .filter_by(app_name=app_name)
                       .one())
    except sqlalchemy.orm.exc.NoResultFound:
        raise RepoException('No entry found for project "%s" in '
                            'the PackageLocations table' % app_name)


def find_app_package(project, app_id):
    """Find a specific mapping between a given project and app type"""

    pass

    # This is no longer valid
    # try:
    #     return (Session.query(AppPackages)
    #                    .filter_by(pkgLocationID=pkg_location_id)
    #                    .filter_by(AppID=app_id)
    #                    .one())
    # except sqlalchemy.orm.exc.NoResultFound:
    #     raise RepoException('No entry with pkgLocationID "%s" and '
    #                         'AppID "%s" found in AppPakcages table'
    #                         % (pkg_location_id, app_id))


def find_app_packages_mapping(app_name):
    """Find all app types related to a given package"""

    app_defs = (Session.query(AppDefinitions)
                       .filter(AppDefinitions.package_locations.any(
                               pkg_name=app_name))
                       .all())

    if not app_defs:
        raise RepoException('No entries found for project "%s" in '
                            'the app_packages table' % app_name)

    return app_defs


def find_project_type(project):
    """Determine the project type for a given project"""

    try:
        return (Session.query(PackageLocations.project_type)
                       .filter_by(app_name=project)
                       .one())
    except sqlalchemy.orm.exc.NoResultFound:
        raise RepoException('No project "%s" found in the '
                            'package_locations table' % project)


def list_app_locations(app_names):
    """ """

    list_query = Session.query(PackageLocations)

    if app_names is not None:
        list_query = \
            list_query.filter(PackageLocations.app_name.in_(app_names))

    return list_query.order_by(PackageLocations.app_name).all()