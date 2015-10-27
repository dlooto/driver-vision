#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 27, 2015, by Junn
#
from vision.gui import new_demo

'''运行Vision Trial 程序'''

from django.core.management.base import BaseCommand
    
class Command(BaseCommand):
    
    help = "Run vision trial Gui"
    
    def handle(self, *args, **options):
        new_demo()
