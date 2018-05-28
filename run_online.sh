#!/usr/bin/bash
vv=$1
regexp='^[0-9]*(\.[0-9]*)?$'
if [[ $vv = *[0-9]* && $vv =~ $regexp ]]; then
    echo "版本号为: $vv"
else
    echo "'$vv' 请输入一个合法数字做版本号"
    exit
fi
vv="v${vv}"
work_path=/data/usr/local/superset_v2.0

export SUPERSET_CONFIG_PATH="/data/usr/local/superset_v2.0/$vv/superset/superset/config_ext.py"
cd $work_path&&sed -i "s/\/v[0-9\.]*/\/$vv/g" ./uwsgi.ini&&mkdir $vv&&cd $vv
git clone ssh://qiwenbao@gerrit.dev.aixuexi.com:29418/superset --depth=1
git clone ssh://qiwenbao@gerrit.dev.aixuexi.com:29418/supersetJSDeploy --depth=1
cp -r ./supersetJSDeploy/dist ./superset/superset/static/assets/
cd superset
tar -zxvf superset.tar.gz
#mv superset temp
#mv temp/* .
ln -s $work_path/lib/python3.6/site-packages/flask_appbuilder/static/appbuilder $work_path/$vv/superset/superset/static

upid=$(sudo netstat -nlp | grep :15801 | awk '{print $7}' | awk -F"/" '{ print $1 }')
if [ ! $upid ]; then
    echo "启动uwsgi"
    $work_path/bin/uwsgi --ini $work_path/uwsgi.ini
else
    echo "重启uwsgi"
    $work_path/bin/uwsgi --reload $work_path/wsgi.pid
fi
#sudo kill -9 $upid

pkill -9 -f 'celery worker'
celery --workdir=$work_path/$vv/superset -A superset.sql_lab.celery_app  worker -l INFO -D -f $work_path/$vv/superset/celery.log --pidfile=$work_path/$vv/superset/celery.pid

sudo sed -i "s/\/v[0-9\.]*/\/$vv/g" /etc/nginx/conf.d/python.conf
sudo service nginx restart


