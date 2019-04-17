pid=$(cat /var/log/ices/ices.pid)
sudo kill -9 $pid
sudo rm -rf /var/log/ices/ices.pid
