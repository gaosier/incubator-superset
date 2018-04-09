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

cd /data/usr/local/superset&&sed -i "s/\/v[0-9\.]*/\/$vv/g" ./uwsgi.ini&&cd $vv

upid=$(sudo netstat -nlp | grep :15801 | awk '{print $7}' | awk -F"/" '{ print $1 }')
if [ ! $upid ]; then
    echo "启动uwsgi"
    uwsgi --ini /data/usr/local/superset/uwsgi.ini
else
    echo "重启uwsgi"
    uwsgi --reload /data/usr/local/superset/wsgi.pid
fi
#sudo kill -9 $upid

pkill -9 -f 'celery worker'
celery --workdir=/data/usr/local/superset/$vv/superset -A superset.sql_lab.celery_app  worker -l INFO -D -f /data/usr/local/superset/$vv/superset/celery.log --pidfile=/data/usr/local/superset/$vv/superset/celery.pid
echo "启动celery"

sudo sed -i "s/\/v[0-9\.]*/\/$vv/g" /etc/nginx/conf.d/python.conf
sudo service nginx restart

