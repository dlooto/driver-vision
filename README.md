## vision readme

====vision cmd:
2vt
run8                        ---admin后台
run_trial                   ---Demo run

access: http://localhost:8000/admin         ---view Data here

===following installed
e:  
  vt_work
  Python27
  Git
  
C: MySQL

==本地程序库目录
Python27/Lib/site-packages/django/contrib/admin/sites.py

==MySQL脚本执行
cmd
mysql -u root -p
>>Enter password:
use vision;
>>execute sql 

==更新代码
2vt
cd ..
git pull
--->若出现错误, 注意查看错误信息, 将有改动的本地文件备份后删除. 重新执行:
git pull

==启动运动worker
python manage.py celery worker --loglevel=info --settings=settings.local

>>>运行环境构建
virtualenv, mysql, git
pip, python, django1.5.1
python-mysql, suit,  
#pull code:  ssh-key

==ssh-agent
若执行ssh-add /path/to/xxx.pem是出现这个错误:Could not open a connection to your authentication agent，则先执行如下命令即可：
　　ssh-agent bash          - - 有错, 采用如下:
   eval `ssh-agent`


==pip install 
pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

==tools install 
http://www.codegood.com/archives/129    --MySQL-python for windows
http://dev.mysql.com/downloads/file/?id=461390    --mysql for windows














==