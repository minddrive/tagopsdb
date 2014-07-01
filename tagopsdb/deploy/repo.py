import sqlalchemy.orm.exc

from sqlalchemy import func

from tagopsdb.model import Session
from tagopsdb.model import (
    AppDefinition, PackageDefinition, PackageLocation, PackageName,
    ProjectPackage, Project
)
from tagopsdb.exceptions import RepoException


def add_app_location(project_type, pkg_type, pkg_name, app_name, path, arch,
                     build_host, env_specific):
    """Add the location of a given application"""

    # Ensure the environment parameter is boolean
    env_specific = bool(env_specific)

    project = PackageLocation(
        project_type=project_type,
        pkg_type=pkg_type,
        pkg_name=pkg_name,
        app_name=app_name,
        path=path,
        arch=arch,
        build_host=build_host,
        environment=env_specific
    )
    Session.add(project)
    Session.flush()   # Needed to get pkgLocationID generated

    # Transitional code to synchronize with new tables
    project_new = add_project(app_name)
    pkg_def = add_package_definition('rpm', 'matching', pkg_name,
                                     path, arch, 'jenkins', build_host,
                                     env_specific)
    Session.add(pkg_def)
    Session.flush()   # Needed to get pkg_def_id generated

    package_name = PackageName(name=pkg_name, pkg_def_id=pkg_def.id)
    Session.add(package_name)
    pkg_def.package_names.append(package_name)

    return project, project_new, pkg_def


def add_app_packages_mapping(project, project_new, pkg_def, app_types):
    """Add the mappings of the app types for a given project"""

    for app_type in app_types:
        try:
            app_def = (Session.query(AppDefinition)
                              .filter_by(app_type=app_type)
                              .one())
        except sqlalchemy.orm.exc.NoResultFound:
            raise RepoException('App type "%s" is not found in the '
                                'Application table' % app_type)

        project.app_definitions.append(app_def)

        # Transitional code to synchronize with new tables
        proj_pkg = ProjectPackage()
        proj_pkg.projects = project_new
        proj_pkg.package_definitions = pkg_def
        proj_pkg.app_definitions = app_def
        Session.add(proj_pkg)


def add_package_definition(deploy_type, validation_type, name, path,
                           arch, build_type, build_host, env_specific):
    """Add base definition for a package"""

    pkg_def = PackageDefinition(
        deploy_type=deploy_type,
        validation_type=validation_type,
        pkg_name=name,
        path=path,
        arch=arch,
        build_type=build_type,
        build_host=build_host,
        env_specific=env_specific,
        created=func.current_timestamp()
    )
    Session.add(pkg_def)

    Session.flush()   # Needed to get pkg_ef_id generated

    return pkg_def


def add_project(name):
    """Add a new project to the database"""

    project = Project(name=name)
    Session.add(project)

    Session.flush()   # Needed to get project_id generated

    return project


def delete_app_location(app_name):
    """Delete the location of a given application"""

    try:
        pkg_loc = find_app_location(app_name)
    except sqlalchemy.orm.exc.NoResultFound:
        raise RepoException('No application "%s" to remove from '
                            'PackageLocation table' % app_name)

    Session.delete(pkg_loc)


def delete_app_packages_mapping(project, app_types):
    """Delete the mappings of the app types for a given project"""

    for app_type in app_types:
        try:
            app_def = (Session.query(AppDefinition)
                              .filter_by(app_type=app_type)
                              .one())
        except sqlalchemy.orm.exc.NoResultFound:
            raise RepoException('App type "%s" is not found in the '
                                'Application table' % app_type)

        project.app_definitions.remove(app_def)


def find_app_location(app_name):
    """Find a given project"""

    try:
        return (Session.query(PackageLocation)
                       .filter_by(app_name=app_name)
                       .one())
    except sqlalchemy.orm.exc.NoResultFound:
        raise RepoException('No entry found for project "%s" in '
                            'the PackageLocation table' % app_name)


def find_app_package(project, app_id):
    """Find a specific mapping between a given project and app type"""

    pass

    # This is no longer valid
    # try:
    #     return (Session.query(AppPackage)
    #                    .filter_by(pkgLocationID=pkg_location_id)
    #                    .filter_by(AppID=app_id)
    #                    .one())
    # except sqlalchemy.orm.exc.NoResultFound:
    #     raise RepoException('No entry with pkgLocationID "%s" and '
    #                         'AppID "%s" found in AppPakcages table'
    #                         % (pkg_location_id, app_id))


def find_app_packages_mapping(app_name):
    """Find all app types related to a given package"""

    app_defs = (Session.query(AppDefinition)
                       .filter(AppDefinition.package_locations.any(
                               pkg_name=app_name))
                       .all())

    if not app_defs:
        raise RepoException('No entries found for project "%s" in '
                            'the app_packages table' % app_name)

    return app_defs


def find_project(name):
    """Find a given project"""

    try:
        return (Session.query(Project)
                       .filter_by(name=name)
                       .one())
    except sqlalchemy.orm.exc.NoResultFound:
        raise RepoException('No entry found for project "%s" in '
                            'the Project table' % name)


def find_project_type(project):
    """Determine the project type for a given project"""

    try:
        return (Session.query(PackageLocation.project_type)
                       .filter_by(app_name=project)
                       .one())
    except sqlalchemy.orm.exc.NoResultFound:
        raise RepoException('No project "%s" found in the '
                            'package_locations table' % project)


def list_app_locations(app_names):
    """ """

    list_query = Session.query(PackageLocation)

    if app_names is not None:
        list_query = \
            list_query.filter(PackageLocation.app_name.in_(app_names))

    return list_query.order_by(PackageLocation.app_name).all()
