# yum-autoclean - Yum plugin for cleaning up old packages in cache
# Copyright (C) 2013  Arnel A. Borja <kyoushuu@yahoo.com>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import os.path

from yum import misc, logginglevels
from yum.plugins import TYPE_INTERACTIVE
from yum.packages import YumLocalPackage


requires_api_version = '2.5'
plugin_type = (TYPE_INTERACTIVE,)


class AutocleanCommand:
    def getNames(self):
        return ['autoclean']

    def getUsage(self):
        return ""

    def getSummary(self):
        return "Clean up old packages in cache"

    def doCheck(self, base, basecmd, extcmds):
        pass

    def doCommand(self, base, basecmd, extcmds):
        removed = 0
        for repo in base.repos.listEnabled():
            base.verbose_logger.log(logginglevels.INFO_2,
                'Cleaning up %s repository', repo)
            packages = []

            path = getattr(repo, 'pkgdir')
            if os.path.exists(path) and os.path.isdir(path):
                for item in misc.getFileList(path, 'rpm', []):
                    try:
                        packages.append(YumLocalPackage(ts=base.ts, filename=item))
                    except:
                        base.logger.critical('Cannot load package file %s', item)
                        continue

            if len(packages) is 0:
                base.verbose_logger.log(logginglevels.INFO_2, '')
                continue

            packages = sorted(packages, key=lambda x: x.name)
            packages = sorted(packages, key=lambda x: x.arch)

            last_package = packages[0]
            for package in packages:
                if last_package.name is not package.name or \
                   last_package.arch is not package.arch:
                    last_package = package
                    continue

                version_cmp = package.verCMP(last_package)
                if version_cmp < 0:
                    older_package = package
                    newer_package = last_package
                elif version_cmp > 0:
                    older_package = last_package
                    newer_package = package
                    last_package = package
                else:
                    last_package = package
                    continue

                base.verbose_logger.log(logginglevels.DEBUG_2,
                    '%s.%s %s is older than %s',
                    older_package.name, older_package.arch,
                    older_package.printVer(), newer_package.printVer())

                try:
                    misc.unlink_f(older_package.localPkg())
                except OSError, e:
                    base.logger.critical('Cannot remove package file %s', older_package.localPkg())
                    continue
                else:
                    removed += 1
                    base.verbose_logger.log(logginglevels.DEBUG_4,
                        'Package file %s removed', older_package.localPkg())

            base.verbose_logger.log(logginglevels.INFO_2, '')
        return 0, ['%d packages removed' % removed]


def config_hook(conduit):
    '''
Add the 'autoclean' command.
'''
    conduit.registerCommand(AutocleanCommand())
