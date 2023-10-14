#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License Version 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright (C) 2007 S.Çağlar Onur <caglar@pardus.org.tr>
# Copyright (C) 2013 Ikey Doherty <ikey@solusos.com>
<<<<<<< HEAD
# Copyright (C) 2021 Berk Çakar <berk2238@hotmail.com>
=======
>>>>>>> origin/main

# Notes to PiSi based distribution maintainers
# /etc/PackageKit/pisi.conf must contain a mapping of PiSi component to
# PackageKit groups for correct operation, i.e.
#   system.utils       = system
#   desktop.gnome      = desktop-gnome
# If you have a BTS you must also provide Bug-Regex and Bug-URI fields, i.e:
#   Bug-Regex = Bug-SolusOS: T(\d+)
#   Bug-URI = http://inf.solusos.com/T%s
# We use simple python string formatting to replace the %s with the first
# matched group in the regular expression. So in the example above, we expect
# to see "Bug-SolusOS: T9" for example, on its own line in a package update
# comment.

import pisi
import pisi.ui
from packagekit.backend import *
from packagekit.package import PackagekitPackage
from packagekit import enums
import os.path
import piksemel
<<<<<<< HEAD
from collections import Counter
import re

# Override PiSi UI so we can get callbacks for progress and events
=======
import re

>>>>>>> origin/main
class SimplePisiHandler(pisi.ui.UI):

    def __init(self):
        pisi.ui.UI.__init__(self, False, False)

    def display_progress(self, **ka):
        self.the_callback(**ka)

<<<<<<< HEAD
    def notify(self, event, **keywords):
        self.pisi_status(event, **keywords)

class PackageKitPisiBackend(PackageKitBaseBackend, PackagekitPackage):

    SETTINGS_FILE = "/etc/PackageKit/pisi.d/groups.list"
=======

class PackageKitPisiBackend(PackageKitBaseBackend, PackagekitPackage):

    SETTINGS_FILE = "/etc/PackageKit/pisi.conf"
>>>>>>> origin/main

    def __init__(self, args):
        self.bug_regex = None
        self.bug_uri = None
        self._load_settings()
        PackageKitBaseBackend.__init__(self, args)

        self.componentdb = pisi.db.componentdb.ComponentDB()
<<<<<<< HEAD
        # self.filesdb = pisi.db.filesdb.FilesDB()
        self.installdb = pisi.db.installdb.InstallDB()
        self.packagedb = pisi.db.packagedb.PackageDB()
        self.historydb = pisi.db.historydb.HistoryDB()
=======
        self.filesdb = pisi.db.filesdb.FilesDB()
        self.installdb = pisi.db.installdb.InstallDB()
        self.packagedb = pisi.db.packagedb.PackageDB()
>>>>>>> origin/main
        self.repodb = pisi.db.repodb.RepoDB()

        # Do not ask any question to users
        self.options = pisi.config.Options()
        self.options.yes_all = True

        self.saved_ui = pisi.context.ui

    def _load_settings(self):
        """ Load the PK Group-> PiSi component mapping """
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, "r") as mapping:
                self.groups = {}
                for line in mapping.readlines():
                    line = line.replace("\r", "").replace("\n", "").strip()
                    if line.strip() == "" or "#" in line:
                        continue

                    splits = line.split("=")
                    key = splits[0].strip()
                    value = splits[1].strip()

                    # Check if this contains our bug keys
                    if key == "Bug-Regex":
                        self.bug_regex = re.compile(value)
                        continue
                    if key == "Bug-URI":
                        self.bug_uri = value
                        continue
                    self.groups[key] = value
        else:
            self.groups = {}

    def __get_package_version(self, package):
        """ Returns version string of given package """
        # Internal FIXME: PiSi may provide this
        if package.build is not None:
            version = "%s-%s-%s" % (package.version, package.release,
                                    package.build)
        else:
            version = "%s-%s" % (package.version, package.release)
        return version

    def __get_package(self, package, filters=None):
        """ Returns package object suitable for other methods """
<<<<<<< HEAD

        status = INFO_AVAILABLE
        data = "installed"
        pkg = ""

        installed = self.installdb.get_package(package) if self.installdb.has_package(package) else None
        available, repo = self.packagedb.get_package_repo(package) if self.packagedb.has_package(package) else (None, None)

        # Not found
        if installed is None and available is None:
            self.error(ERROR_PACKAGE_NOT_FOUND, "Package %s was not found" % package)

        # Unholy matrimony of irish priests who got a deal with the catholic church
        fltred = None
        fltr_status = None
        fltr_data = None
        if filters is not None:
            if FILTER_NOT_INSTALLED in filters:
                fltred = available if available is not None else None
                if fltred is None:
                    return
                fltr_status = INFO_AVAILABLE if fltred is not None else None
                fltr_data = repo if fltred is not None else None
            if FILTER_INSTALLED in filters:
                fltred = installed if installed is not None else None
                if fltred is None:
                    return
                fltr_status = INFO_INSTALLED if fltred is not None else None
                fltr_data = "installed:{}".format(repo) if repo is not None else data
            # FIXME: Newest should be able to show the newest local version as well as remote version
            if FILTER_NEWEST in filters:
                fltred = available if available is not None else installed
                fltr_status = INFO_AVAILABLE if fltred is not None else None
                fltr_data = repo if fltred is not None else None
            if FILTER_NEWEST in filters and FILTER_INSTALLED in filters:
                fltred = installed if installed is not None else None
                fltr_status = INFO_INSTALLED if fltred is not None else None
                fltr_data = "installed:{}".format(repo) if repo is not None else data

        # Installed and has repo origin
        if available is not None and installed is not None:
            pkg = fltred if fltred is not None else installed
            status = fltr_status if fltr_status is not None else INFO_INSTALLED
            data = fltr_data if fltr_data is not None else "installed:{}".format(repo)

        # Available but not installed
        if available is not None and installed is None:
            pkg = fltred if fltred is not None else available
            status = fltr_status if fltr_status is not None else INFO_AVAILABLE
            data = fltr_data if fltr_data is not None else repo

        # Installed but has no repo origin
        if installed is not None and available is None:
            pkg = fltred if fltred is not None else installed
            status = fltr_status if fltr_status is not None else INFO_INSTALLED
            data = fltr_data if fltr_data is not None else "installed"

        if filters is not None:
            if FILTER_GUI in filters and "app:gui" not in pkg.isA:
                return
            if FILTER_NOT_GUI in filters and "app:gui" in pkg.isA:
                return
            # FIXME: To lower
            nonfree = ['EULA', 'Distributable']
            if FILTER_FREE in filters:
                if any(l in pkg.license for l in nonfree):
                    return
            if FILTER_NOT_FREE in filters:
                if not any(l in pkg.license for l in nonfree):
                    return
            if FILTER_DEVELOPMENT in filters and not "-devel" in pkg.name:
                return
            if FILTER_NOT_DEVELOPMENT in filters and "-devel" in pkg.name:
                return
            pkg_subtypes = ["-devel", "-dbginfo", "-32bit", "-docs"]
            if FILTER_BASENAME in filters:
                if any(suffix in pkg.name for suffix in pkg_subtypes):
                    return
            if FILTER_NOT_BASENAME in filters:
                if not any(suffix in pkg.name for suffix in pkg_subtypes):
                    return

        version = self.__get_package_version(pkg)
        id = self.get_package_id(pkg.name, version, pkg.architecture, data)
=======
        if self.installdb.has_package(package):
            status = INFO_INSTALLED
            pkg = self.installdb.get_package(package)
        elif self.packagedb.has_package(package):
            status = INFO_AVAILABLE
            pkg = self.packagedb.get_package(package)
        else:
            self.error(ERROR_PACKAGE_NOT_FOUND, "Package was not found")

        if filters:
            if "none" not in filters:
                if FILTER_INSTALLED in filters and status != INFO_INSTALLED:
                    return
                if FILTER_NOT_INSTALLED in filters and status == INFO_INSTALLED:
                    return
                if FILTER_GUI in filters and "app:gui" not in pkg.isA:
                    return
                if FILTER_NOT_GUI in filters and "app:gui" in pkg.isA:
                    return

        version = self.__get_package_version(pkg)

        id = self.get_package_id(pkg.name, version, pkg.architecture, "")

>>>>>>> origin/main
        return self.package(id, status, pkg.summary)

    def depends_on(self, filters, package_ids, recursive):
        """ Prints a list of depends for a given package """
<<<<<<< HEAD
        self.status(STATUS_QUERY)
        self.allow_cancel(True)
        self.percentage(None)

        for package_id in package_ids:
            package = self.get_package_from_id(package_id)[0]

            # FIXME: PiSi API has really inconsistent for return types and arguments!
            if self.packagedb.has_package(package):
                for pkg in self.packagedb.get_package(package).runtimeDependencies():
                    self.__get_package(pkg.package)
            elif self.installdb.has_package(package):
                for pkg in self.installdb.get_package(package).runtimeDependencies():
                    self.__get_package(pkg.package)
            else:
                self.error(ERROR_PACKAGE_NOT_FOUND, "Package %s was not found" % package)

    def get_categories(self):
        self.status(STATUS_QUERY)
        self.allow_cancel(True)
        categories = self.componentdb.list_components()
        categories.sort()

        for p in categories:
            component = self.componentdb.get_component(p)

            #group_img = "/usr/share/icons/Adwaita/symbolic/categories/applications-%s-symbolic.svg" % (component.name)
            #if os.path.isfile(group_img) and os.access(group_img, os.R_OK):
            #    icon = group_img
            #else:
            #    icon = "image-missing"

            cat_id = component.name  # same thing
            self.category(component.group, cat_id, component.name, unicode(component.summary), "image-missing")

    def repair_system(self, transaction_flags):
        '''
        Implement the {backend}-repair-system functionality
        Needed to be implemented in a sub class
        '''
        self.error(ERROR_NOT_SUPPORTED, "This function is not implemented in this backend",
                   exit=False)

    def get_details(self, package_ids):
        """ Prints a detailed description for a given packages """
        self.status(STATUS_QUERY)
        self.allow_cancel(True)
        self.percentage(None)

        for package in package_ids:
            package = self.get_package_from_id(package)[0]

            pkg = ""
            size = 0
            data = "installed"

            # FIXME: There is duplication here from __get_package
            if self.packagedb.has_package(package):
                pkg, repo = self.packagedb.get_package_repo(package, None)
                if self.installdb.has_package(package):
                    local_pkg = self.installdb.get_package(package)
                    size = int(local_pkg.installedSize)
                else:
                    size = int(pkg.packageSize)
                if self.installdb.has_package(package):
                    data = "installed:{}".format(repo)
                else:
                    data = repo
            elif self.installdb.has_package(package):
                pkg = self.installdb.get_package(package)
                data = "local"
                size = int(pkg.installedSize)
            else:
                self.error(ERROR_PACKAGE_NOT_FOUND, "Package %s was not found" % package)


            pkg_id = self.get_package_id(pkg.name, self.__get_package_version(pkg),
                                            pkg.architecture, data)
=======
        self.allow_cancel(True)
        self.percentage(None)

        package = self.get_package_from_id(package_ids[0])[0]

        for pkg in self.packagedb.get_package(package).runtimeDependencies():
            # FIXME: PiSi API has really inconsistent for return types
            # and arguments!
            self.__get_package(pkg.package)

    def get_details(self, package_ids):
        """ Prints a detailed description for a given package """
        self.allow_cancel(True)
        self.percentage(None)

        package = self.get_package_from_id(package_ids[0])[0]

        if self.packagedb.has_package(package):
            pkg = self.packagedb.get_package(package)
            repo = self.packagedb.get_package_repo(pkg.name, None)
            pkg_id = self.get_package_id(pkg.name,
                                         self.__get_package_version(pkg),
                                         pkg.architecture, repo[1])
>>>>>>> origin/main

            if pkg.partOf in self.groups:
                group = self.groups[pkg.partOf]
            else:
                group = GROUP_UNKNOWN
<<<<<<< HEAD
            homepage = pkg.source.homepage if pkg.source.homepage is not None\
                else ''

            self.details(pkg_id, pkg.summary, ",".join(pkg.license), group, pkg.description,
                            homepage, size)

    def get_details_local(self, files):

        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_INFO)

        for f in files:
            if not f.endswith(".eopkg"):
                self.error(ERROR_PACKAGE_NOT_FOUND, "Eopkg %s was not found" % f)
            try:
                metadata, files = pisi.api.info_file(f)
            except PkError, e:
                if e.code == ERROR_PACKAGE_NOT_FOUND:
                    self.message('COULD_NOT_FIND_PACKAGE', e.details)
                    continue
                self.error(e.code, e.details, exit=True)
                return
            if metadata:
                pkg = metadata.package

            data = "local"

            pkg_id = self.get_package_id(pkg.name, self.__get_package_version(pkg),
                                            pkg.architecture, data)

            if pkg.partOf in self.groups:
                group = self.groups[pkg.partOf]
            else:
                group = GROUP_UNKNOWN
            homepage = pkg.source.homepage if pkg.source.homepage is not None\
                else ''

            size = pkg.installedSize

            self.details(pkg_id, pkg.summary, ",".join(pkg.license), group, pkg.description,
                            homepage, size)

    def get_files(self, package_ids):
        """ Prints a file list for a given packages """
        self.allow_cancel(True)
        self.percentage(None)

        for package_id in package_ids:
            package = self.get_package_from_id(package_id)[0]

            if self.installdb.has_package(package):
                pkg = self.packagedb.get_package(package)
                repo = self.packagedb.get_package_repo(pkg.name, None)
                pkg_id = self.get_package_id(pkg.name,
                                            self.__get_package_version(pkg),
                                            pkg.architecture, repo[1])

                pkg = self.installdb.get_files(package)

                files = map(lambda y: "/%s" % y.path, pkg.list)

                file_list = ";".join(files)
                self.files(pkg_id, file_list)
            else:
                self.error(ERROR_PACKAGE_NOT_FOUND,
                           "Package %s must be installed to get file list" % package_id.split(";"))

    def get_packages(self, filters):
        self.status(STATUS_QUERY)
        self.allow_cancel(True)
        self.percentage(None)

        packages = list()
        all_pkgs = False
        installed = self.installdb.list_installed()
        available = self.packagedb.list_packages(None)

        if FILTER_INSTALLED in filters:
            packages = installed
        elif FILTER_NOT_INSTALLED in filters:
            cntInstalled = Counter(installed)
            cntAvailable = Counter(available)

            diff = cntAvailable - cntInstalled
            packages = diff.elements()
        else:
            #since = self.historydb.get_last_repo_update()
            #packages = self.packagedb.list_newest(None, since)
            packages = available

        for package in packages:
            self.__get_package(package)

        self.percentage(100)
=======

            homepage = pkg.source.homepage if pkg.source.homepage is not None\
                else ''

            self.details(pkg_id, '', ",".join(pkg.license), group, pkg.description,
                         homepage, pkg.packageSize)
        else:
            self.error(ERROR_PACKAGE_NOT_FOUND, "Package was not found")

    def get_files(self, package_ids):
        """ Prints a file list for a given package """
        self.allow_cancel(True)
        self.percentage(None)

        package = self.get_package_from_id(package_ids[0])[0]

        if self.installdb.has_package(package):
            pkg = self.packagedb.get_package(package)
            repo = self.packagedb.get_package_repo(pkg.name, None)
            pkg_id = self.get_package_id(pkg.name,
                                         self.__get_package_version(pkg),
                                         pkg.architecture, repo[1])

            pkg = self.installdb.get_files(package)

            files = map(lambda y: "/%s" % y.path, pkg.list)

            file_list = ";".join(files)
            self.files(pkg_id, file_list)
>>>>>>> origin/main

    def get_repo_list(self, filters):
        """ Prints available repositories """
        self.allow_cancel(True)
        self.percentage(None)
<<<<<<< HEAD
        self.status(STATUS_INFO)

        for repo in self.repodb.list_repos(only_active=False):
            uri = self.repodb.get_repo_url(repo)
            enabled = False
            if self.repodb.repo_active(repo):
                enabled = True
            self.repo_detail(repo, uri, enabled)

    def required_by(self, filters, package_ids, recursive):
        """ Prints a list of requires for a given package """
        self.status(STATUS_QUERY)
        self.allow_cancel(True)
        self.percentage(None)

        for package_id in package_ids:
            package = self.get_package_from_id(package_id)[0]

            if self.packagedb.has_package(package):
                for pkg in self.packagedb.get_rev_deps(package):
                    self.__get_package(pkg[0])
            elif self.installdb.has_package(package):
                for pkg in self.installdb.get_rev_deps(package):
                    self.__get_package(pkg[0])
            else:
                self.error(ERROR_PACKAGE_NOT_FOUND, "Package %s was not found" % package.name)
=======

        for repo in pisi.api.list_repos():
            # Internal FIXME: What an ugly way to get repo uri
            # FIXME: Use repository enabled/disabled state
            uri = self.repodb.get_repo(repo).indexuri.get_uri()
            self.repo_detail(repo, uri, True)

    def required_by(self, filters, package_ids, recursive):
        """ Prints a list of requires for a given package """
        self.allow_cancel(True)
        self.percentage(None)

        package = self.get_package_from_id(package_ids[0])[0]

        # FIXME: Handle packages which is not installed from repository
        for pkg in self.packagedb.get_rev_deps(package):
            self.__get_package(pkg[0])
>>>>>>> origin/main

    def get_updates(self, filter):
        """ Prints available updates and types """
        self.allow_cancel(True)
        self.percentage(None)

        self._updates = dict()
        for package in pisi.api.list_upgradable():
<<<<<<< HEAD
            pkg, repo = self.packagedb.get_package_repo(package, None)
            version = self.__get_package_version(pkg)
            id = self.get_package_id(pkg.name, version, pkg.architecture, repo)
            installed_package = self.installdb.get_package(package)
            pindex = "/var/lib/eopkg/index/%s/eopkg-index.xml" % repo
=======
            pkg = self.packagedb.get_package(package)
            version = self.__get_package_version(pkg)
            id = self.get_package_id(pkg.name, version, pkg.architecture, "")
            installed_package = self.installdb.get_package(package)

            repo = self.packagedb.get_package_repo(pkg.name, None)[1]
            pindex = "/var/lib/pisi/index/%s/pisi-index.xml" % repo
>>>>>>> origin/main

            self._updates[pkg.name] = \
                self._extract_update_details(pindex, pkg.name)
            bug_uri = self._updates[pkg.name][3]

            # FIXME: PiSi must provide this information as a single API call :(
            updates = [i for i in self.packagedb.get_package(package).history
                       if pisi.version.Version(i.release) >
                       installed_package.release]
            if pisi.util.any(lambda i: i.type == "security", updates):
                self.package(id, INFO_SECURITY, pkg.summary)
            elif bug_uri != "":
                self.package(id, INFO_BUGFIX, pkg.summary)
            else:
                self.package(id, INFO_NORMAL, pkg.summary)

    def _extract_update_details(self, pindex, package_name):
        document = piksemel.parse(pindex)
        packages = document.tags("Package")
        for pkg in packages:
            if pkg.getTagData("Name") == package_name:
                history = pkg.getTag("History")
                update = history.tags("Update")
                update_message = "Updated"
                update_release = 0
                update_date = ""
                needsReboot = False
                bugURI = ""
                for update in update:
                    if int(update.getAttribute("release")) > update_release:
                        update_release = int(update.getAttribute("release"))
                        # updater = update.getTagData("Name")
                        update_message = update.getTagData("Comment")
                        update_message = update_message.replace("\n", ";")
                        update_date = update.getTagData("Date")
                        needsReboot = False
                        try:
                            requires = update.getTag("Requires")
                            action = requires.getTagData("Action")
                            if action == "systemRestart":
                                needsReboot = True
                        except Exception:
                            pass
                # Determine if this is a bug fix
                for line in update_message.split(";"):
                    m = self.bug_regex.match(line)
                    if m is not None:
                        bugURI = self.bug_uri % m.group(1)
                        break
                return (update_message, update_date, needsReboot, bugURI)
            pkg = pkg.nextTag("Package")
        return("Log not found", "", False, "")

    def get_update_detail(self, package_ids):
<<<<<<< HEAD
        self.status(STATUS_INFO)
        self.allow_cancel(True)
        self.percentage(None)

        for package_id in package_ids:
            package = self.get_package_from_id(package_id)[0]
            pkg, repo = self.packagedb.get_package_repo(package, None)
            version = self.__get_package_version(pkg)
            id = self.get_package_id(pkg.name, version, pkg.architecture, repo)
            pindex = "/var/lib/eopkg/index/%s/eopkg-index.xml" % repo

            updates = [package_id]
            obsoletes = ""
            package_url = pkg.source.homepage
            vendor_url = package_url if package_url is not None else ""

            changelog = ""
            update_message, updated_date, needsReboot, bugURI = \
                self._extract_update_details(pindex, pkg.name)

            cves = re.findall(r" (CVE\-[0-9]+\-[0-9]+)", str(update_message))
            cve_url = ""
            if cves is not None:
                #cve_url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(cves[0])
                cve_url = cves
=======
        for package_id in package_ids:
            package = self.get_package_from_id(package_id)[0]
            the_package = self.installdb.get_package(package)
            updates = [package_id]
            obsoletes = ""
            # TODO: Add regex matching for #FIXES:ID or something similar
            cve_url = ""
            package_url = the_package.source.homepage
            vendor_url = package_url if package_url is not None else ""
            issued = ""

            changelog = ""
            # TODO: Set to security_issued if security update
            issued = updated = ""
            update_message, security_issued, needsReboot, bugURI = \
                self._updates[package]
>>>>>>> origin/main

            # TODO: Add tagging to repo's, or a mapping file
            state = UPDATE_STATE_STABLE
            reboot = "system" if needsReboot else "none"

<<<<<<< HEAD
            # TODO: Eopkg doesn't provide any time
            split_date = updated_date.split("-")
            updated = "{}-{}-{}T00:00:00".format(split_date[0], split_date[1], split_date[2])
            issued = ""

=======
>>>>>>> origin/main
            self.update_detail(package_id, updates, obsoletes, vendor_url,
                               bugURI, cve_url, reboot, update_message,
                               changelog, state, issued, updated)

    def download_packages(self, directory, package_ids):
        """ Download the given packages to a directory """
<<<<<<< HEAD
        self.allow_cancel(True)
        self.percentage(0)
=======
        self.allow_cancel(False)
        self.percentage(None)
>>>>>>> origin/main
        self.status(STATUS_DOWNLOAD)

        packages = list()

        def progress_cb(**kw):
            self.percentage(int(kw['percent']))

<<<<<<< HEAD
        def status_cb(event, **keywords):
            if event == pisi.ui.downloading:
                self.package(package_id, INFO_DOWNLOADING, pkg.summary)

=======
>>>>>>> origin/main
        ui = SimplePisiHandler()
        for package_id in package_ids:
            package = self.get_package_from_id(package_id)[0]
            packages.append(package)
            try:
                pkg = self.packagedb.get_package(package)
            except:
                self.error(ERROR_PACKAGE_NOT_FOUND, "Package was not found")
        try:
            pisi.api.set_userinterface(ui)
            ui.the_callback = progress_cb
<<<<<<< HEAD
            ui.pisi_status = status_cb
=======
>>>>>>> origin/main
            if directory is None:
                directory = os.path.curdir
            pisi.api.fetch(packages, directory)
            # Scan for package
            for package in packages:
                package_obj = self.packagedb.get_package(package)
                uri = package_obj.packageURI.split("/")[-1]
                location = os.path.join(directory, uri)
                self.files(package_id, location)
            pisi.api.set_userinterface(self.saved_ui)
        except Exception, e:
            self.error(ERROR_PACKAGE_DOWNLOAD_FAILED,
                       "Could not download package: %s" % e)
<<<<<<< HEAD
        self.finished()
=======
        self.percentage(None)
>>>>>>> origin/main

    def install_files(self, only_trusted, files):
        """ Installs given package into system"""

        # FIXME: use only_trusted
<<<<<<< HEAD
=======

>>>>>>> origin/main
        # FIXME: install progress
        self.allow_cancel(False)
        self.percentage(None)

<<<<<<< HEAD
        def status_cb(event, **keywords):
            if event == pisi.ui.extracting or event == pisi.ui.installing:
                self.status(STATUS_INSTALL)
                self.package(package_id, INFO_INSTALLING, pkg.summary)

        ui = SimplePisiHandler()
        pisi.api.set_userinterface(ui)

        ui.pisi_status = status_cb

        try:
            # Actually install
=======
        def progress_cb(**kw):
            self.percentage(int(kw['percent']))

        ui = SimplePisiHandler()

        self.status(STATUS_INSTALL)
        pisi.api.set_userinterface(ui)
        ui.the_callback = progress_cb

        try:
            self.status(STATUS_INSTALL)
>>>>>>> origin/main
            pisi.api.install(files)
        except pisi.Error, e:
            # FIXME: Error: internal-error : Package re-install declined
            # Force needed?
            self.error(ERROR_PACKAGE_ALREADY_INSTALLED, e)
<<<<<<< HEAD

        pisi.api.set_userinterface(self.saved_ui)
        self.percentage(100)
=======
        pisi.api.set_userinterface(self.saved_ui)
>>>>>>> origin/main

    def _report_all_for_package(self, package, remove=False):
        """ Report all deps for the given package """
        if not remove:
            deps = self.packagedb.get_package(package).runtimeDependencies()
            # TODO: Add support to report conflicting packages requiring removal
            #conflicts = self.packagedb.get_package (package).conflicts
            for dep in deps:
                if not self.installdb.has_package(dep.name()):
                    dep_pkg = self.packagedb.get_package(dep.name())
                    repo = self.packagedb.get_package_repo(dep_pkg.name, None)
                    version = self.__get_package_version(dep_pkg)
                    pkg_id = self.get_package_id(dep_pkg.name, version,
                                                 dep_pkg.architecture, repo[1])
                    self.package(pkg_id, INFO_INSTALLING, dep_pkg.summary)
        else:
            rev_deps = self.installdb.get_rev_deps(package)
            for rev_dep, depinfo in rev_deps:
                if self.installdb.has_package(rev_dep):
                    dep_pkg = self.packagedb.get_package(rev_dep)
                    repo = self.packagedb.get_package_repo(dep_pkg.name, None)
                    version = self.__get_package_version(dep_pkg)
                    pkg_id = self.get_package_id(dep_pkg.name, version,
                                                 dep_pkg.architecture, repo[1])
                    self.package(pkg_id, INFO_REMOVING, dep_pkg.summary)

    def install_packages(self, transaction_flags, package_ids):
        """ Installs given package into system"""
<<<<<<< HEAD

        # FIXME: better fetch/install progress e.g. divide by len of packages
        self.allow_cancel(True)
=======
        # FIXME: fetch/install progress
        self.allow_cancel(False)
>>>>>>> origin/main
        self.percentage(None)

        packages = list()

        # FIXME: use only_trusted
        for package_id in package_ids:
            package = self.get_package_from_id(package_id)[0]
            if self.installdb.has_package(package):
                self.error(ERROR_PACKAGE_NOT_INSTALLED,
                           "Package is already installed")
            packages.append(package)

        def progress_cb(**kw):
            self.percentage(int(kw['percent']))

<<<<<<< HEAD
        def status_cb(event, **keywords):
            # FIXME: Ugly package splitting
            split_id = package_id.split(";", 4)
            pkg = self.packagedb.get_package(split_id[0])
            if event == pisi.ui.downloading:
                self.status(STATUS_DOWNLOAD)
                self.package(package_id, INFO_DOWNLOADING, pkg.summary)
            elif event == pisi.ui.extracting or event == pisi.ui.installing:
                self.status(STATUS_INSTALL)
                self.percentage(None)
                self.allow_cancel(False)
                self.package(package_id, INFO_INSTALLING, pkg.summary)

        ui = SimplePisiHandler()
        pisi.api.set_userinterface(ui)

        ui.the_callback = progress_cb
        ui.pisi_status = status_cb

        if TRANSACTION_FLAG_SIMULATE in transaction_flags:
            for package in packages:
                self._report_all_for_package(package)
            return

        if TRANSACTION_FLAG_ONLY_DOWNLOAD in transaction_flags:
            pisi.context.set_option("fetch_only", True)

=======
        ui = SimplePisiHandler()

        self.status(STATUS_INSTALL)
        pisi.api.set_userinterface(ui)
        ui.the_callback = progress_cb

        if TRANSACTION_FLAG_SIMULATE in transaction_flags:
            # Simulated, not real.
            for package in packages:
                self._report_all_for_package(package)
            return
>>>>>>> origin/main
        try:
            pisi.api.install(packages)
        except pisi.Error, e:
            self.error(ERROR_UNKNOWN, e)
<<<<<<< HEAD

        pisi.api.set_userinterface(self.saved_ui)
        self.finished()
=======
        pisi.api.set_userinterface(self.saved_ui)
>>>>>>> origin/main

    def refresh_cache(self, force):
        """ Updates repository indexes """
        # TODO: use force ?
        self.allow_cancel(False)
        self.percentage(0)
        self.status(STATUS_REFRESH_CACHE)

        slice = (100 / len(pisi.api.list_repos())) / 2

        percentage = 0
        for repo in pisi.api.list_repos():
            pisi.api.update_repo(repo)
            percentage += slice
            self.percentage(percentage)

        self.percentage(100)

    def remove_packages(self, transaction_flags, package_ids,
                        allowdeps, autoremove):
        """ Removes given package from system"""
<<<<<<< HEAD
        # FIXME: better remove progress e.g. get len of pkgs, get len of files per pkg
        # get callback for extra autoremove deps
        self.allow_cancel(False)
        self.percentage(None)
=======
        self.allow_cancel(False)
        self.percentage(None)
        # TODO: use autoremove
>>>>>>> origin/main
        packages = list()

        for package_id in package_ids:
            package = self.get_package_from_id(package_id)[0]
            if not self.installdb.has_package(package):
                self.error(ERROR_PACKAGE_NOT_INSTALLED,
                           "Package is not installed")
            packages.append(package)

<<<<<<< HEAD
        # Callback from pisi events
        def status_cb(event, **keywords):
            # FIXME: Ugly package splitting
            split_id = package_id.split(";", 4)
            pkg = self.packagedb.get_package(split_id[0])
            if event == pisi.ui.removing:
                self.status(STATUS_REMOVE)
                self.package(package_id, INFO_REMOVING, pkg.summary)

        ui = SimplePisiHandler()
        pisi.api.set_userinterface(ui)

        ui.pisi_status = status_cb
=======
        def progress_cb(**kw):
            self.percentage(int(kw['percent']))

        ui = SimplePisiHandler()

        package = self.get_package_from_id(package_ids[0])[0]
        self.status(STATUS_REMOVE)
>>>>>>> origin/main

        if TRANSACTION_FLAG_SIMULATE in transaction_flags:
            # Simulated, not real.
            for package in packages:
                self._report_all_for_package(package, remove=True)
            return
        try:
<<<<<<< HEAD
            if autoremove:
                pisi.api.autoremove(packages)
            else:
                pisi.api.remove(packages)
        except pisi.Error, e:
            self.error(ERROR_CANNOT_REMOVE_SYSTEM_PACKAGE, e)

        pisi.api.set_userinterface(self.saved_ui)
        self.finished()

    def repo_enable(self, repoid, enable):
        self.status(STATUS_INFO)
        self.allow_cancel(True)
        self.percentage(None)
        if self.repodb.has_repo(repoid):
            pisi.api.set_repo_activity(repoid, enable)
            return
        else:
            self.error(ERROR_REPO_NOT_FOUND, "Repository %s was not found" % repoid)
=======
            pisi.api.remove(packages)
        except pisi.Error, e:
            self.error(ERROR_CANNOT_REMOVE_SYSTEM_PACKAGE, e)
        pisi.api.set_userinterface(self.saved_ui)
>>>>>>> origin/main

    def repo_set_data(self, repo_id, parameter, value):
        """ Sets a parameter for the repository specified """
        self.allow_cancel(False)
        self.percentage(None)

        if parameter == "add-repo":
            try:
<<<<<<< HEAD
                pisi.api.add_repo(repo_id, value)
=======
                pisi.api.add_repo(repo_id, value, parameter)
>>>>>>> origin/main
            except pisi.Error, e:
                self.error(ERROR_UNKNOWN, e)

            try:
                pisi.api.update_repo(repo_id)
            except pisi.fetcher.FetchError:
                pisi.api.remove_repo(repo_id)
                err = "Could not reach the repository, removing from system"
                self.error(ERROR_REPO_NOT_FOUND, err)
        elif parameter == "remove-repo":
            try:
                pisi.api.remove_repo(repo_id)
            except pisi.Error:
                self.error(ERROR_REPO_NOT_FOUND, "Repository does not exist")
        else:
<<<<<<< HEAD
            self.error(ERROR_NOT_SUPPORTED, "Valid parameters are add-repo and remove-repo")

    def resolve(self, filters, packages):
=======
            self.error(ERROR_NOT_SUPPORTED, "Parameter not supported")

    def resolve(self, filters, package):
>>>>>>> origin/main
        """ Turns a single package name into a package_id
        suitable for the other methods """
        self.allow_cancel(True)
        self.percentage(None)
<<<<<<< HEAD
        self.status(STATUS_QUERY)

        for package in packages:
            pkg = self.get_package_from_id(package)[0]
            try:
                # FIXME: HACKY HACKY
                if filters is not None and FILTER_NEWEST in filters:
                    self.__get_package(pkg, FILTER_NOT_INSTALLED)
                self.__get_package(pkg, filters)
            except Exception:
                self.error(ERROR_PACKAGE_NOT_FOUND, "Package %s not found" % package)
=======

        self.__get_package(package[0], filters)
>>>>>>> origin/main

    def search_details(self, filters, values):
        """ Prints a detailed list of packages contains search term """
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_INFO)

        # Internal FIXME: Use search_details instead of _package when API
        # gains that ability :)
        for pkg in pisi.api.search_package(values):
            self.__get_package(pkg, filters)

    def search_file(self, filters, values):
        """ Prints the installed package which contains the specified file """
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_INFO)

        for value in values:
            # Internal FIXME: Why it is needed?
            value = value.lstrip("/")

            for pkg, files in pisi.api.search_file(value):
                self.__get_package(pkg)

    def search_group(self, filters, values):
        """ Prints a list of packages belongs to searched group """
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_INFO)

        for value in values:
            packages = list()
            for item in self.groups:
                if self.groups[item] == value:
                    try:
                        pkgs = self.componentdb.get_packages(item, walk=False)
                        packages.extend(pkgs)
                    except:
                        self.error(ERROR_GROUP_NOT_FOUND,
                                   "Component %s was not found" % value)
            for pkg in packages:
                self.__get_package(pkg, filters)

    def search_name(self, filters, values):
        """ Prints a list of packages contains search term in its name """
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_INFO)

        for value in values:
            for pkg in pisi.api.search_package([value]):
                self.__get_package(pkg, filters)

    def update_packages(self, transaction_flags, package_ids):
        """ Updates given package to its latest version """

        # FIXME: use only_trusted
<<<<<<< HEAD
        # FIXME: install progress
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_RUNNING)
=======

        # FIXME: fetch/install progress
        self.allow_cancel(False)
        self.percentage(None)
>>>>>>> origin/main

        packages = list()
        for package_id in package_ids:
            package = self.get_package_from_id(package_id)[0]
            if not self.installdb.has_package(package):
                self.error(ERROR_PACKAGE_NOT_INSTALLED,
                           "Cannot update a package that is not installed")
            packages.append(package)

        def progress_cb(**kw):
            self.percentage(int(kw['percent']))

<<<<<<< HEAD
        def status_cb(event, **keywords):
            # FIXME: Ugly package splitting
            split_id = package_id.split(";", 4)
            pkg = self.packagedb.get_package(split_id[0])
            if event == pisi.ui.downloading:
                self.status(STATUS_DOWNLOAD)
                self.package(package_id, INFO_DOWNLOADING, pkg.summary)
            elif event == pisi.ui.extracting or event == pisi.ui.installing:
                self.status(STATUS_INSTALL)
                self.percentage(None)
                self.allow_cancel(False)
                self.package(package_id, INFO_INSTALLING, pkg.summary)

        ui = SimplePisiHandler()
        pisi.api.set_userinterface(ui)

        ui.the_callback = progress_cb
        ui.pisi_status = status_cb
=======
        ui = SimplePisiHandler()
        pisi.api.set_userinterface(ui)
        ui.the_callback = progress_cb
>>>>>>> origin/main

        if TRANSACTION_FLAG_SIMULATE in transaction_flags:
            for package in packages:
                self._report_all_for_package(package)
            return
<<<<<<< HEAD

        if TRANSACTION_FLAG_ONLY_DOWNLOAD in transaction_flags:
            pisi.context.set_option("fetch_only", True)

        try:
            # Actually upgrade
            pisi.api.upgrade(packages)
        except Exception, e:
            self.error(ERROR_UNKNOWN, e)

        pisi.api.set_userinterface(self.saved_ui)
        self.finished()
=======
        try:
            pisi.api.upgrade(packages)
        except pisi.Error, e:
            self.error(ERROR_UNKNOWN, e)
        pisi.api.set_userinterface(self.saved_ui)

    def update_system(self, only_trusted):
        """ Updates all available packages """
        # FIXME: use only_trusted
        # FIXME: fetch/install progress
        self.allow_cancel(False)
        self.percentage(None)

        if not len(pisi.api.list_upgradable()) > 0:
            self.error(ERROR_NO_PACKAGES_TO_UPDATE, "System is already up2date")

        try:
            pisi.api.upgrade(pisi.api.list_upgradable())
        except pisi.Error, e:
            self.error(ERROR_UNKNOWN, e)

>>>>>>> origin/main

def main():
    backend = PackageKitPisiBackend('')
    backend.dispatcher(sys.argv[1:])

if __name__ == "__main__":
    main()
