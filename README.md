#vision readme

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

==本地django目录
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
--->若出现错误, 注意查看错误信息, 将有改动的本地文件备份后删除.重新执行:
git pull