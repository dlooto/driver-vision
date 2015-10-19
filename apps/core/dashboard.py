# -*-coding:utf-8 -*-
"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'core.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('Auth'),
            column=1,
            collapsible=False,
            models=('django.contrib.*',),
        ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _(u'应用列表'),
            collapsible=True,
            column=1,
            css_classes=('collapse closed',),
            exclude=('django.contrib.*',),
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _(u'Team'),
            column=2,
            children=[
                {
                    'title': _(u'团队协作'),
                    'url': 'team',
                    'external': True,
                },
                #{
                #    'title': _(u'用户反馈'),
                #    'url': 'feedbacks/',
                #    'external': True,
                #},
            ]
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Media'),
            column=2,
            children=[
                {
                    'title': _('FileBrowser'),
                    'url': 'filebrowser/browse/',
                    'external': False,
                },
            ]
        ))



        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=15,
            collapsible=False,
            column=3,
        ))
