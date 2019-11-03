# vision readme

因算法控制程序部分较复杂，本程序工程中使用了较多面向对象及设计模式技巧. 为应对复杂的动态多路牌情况, 程序经过数次大规模重构. 学习Python面向对象的朋友, 此程序可作为学习参考.
作者对本程序保留所有权利, 非经许可不得用于商业目的.


### 运行环境构建
```
virtualenv, mysql, git
pip, python, django1.5.1
python-mysql, suit,
#pull code:  ssh-key
```

### 启动运动worker
```
python manage.py celery worker --loglevel=info --settings=settings.local
```

### ssh-agent
若执行ssh-add /path/to/xxx.pem是出现这个错误:Could not open a connection to your authentication agent，则先执行如下命令即可：
　　ssh-agent bash          - - 有错, 采用如下:
   eval `ssh-agent`


### pip install
```
pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
```

Tools install
http://www.codegood.com/archives/129    --MySQL-python for windows
http://dev.mysql.com/downloads/file/?id=461390    --mysql for windows












