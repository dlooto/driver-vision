#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 27, 2015, by Junn
#
from runtests.tests import test_export_excel

'''运行Tests'''

from django.core.management.base import BaseCommand
    
class Command(BaseCommand):
    
    help = "Run Tests"
    
    def handle(self, *args, **options):
        test_export_excel()
