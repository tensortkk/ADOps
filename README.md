## Recommended Configuration
- RAM: 8G or above
- Docker version >= 18.03
- docker-compose

## Start Services

**local host ip**

- ifconfig
- export HOST=

**docker-compose up**

- docker-compose -f docker-compose.yml up -d --remove-orphans
- docker ps | grep kylin or docker-compose ps

**build adops image**
./adops/build.sh
docker run -it -p 7527:7527 -p 8888:8888 -e HOST=${HOST} -v ./adops:/work/adops/ openmldb:adops bash -c "/work/init.sh & jupyter-lab --ip=0.0.0.0 --allow-root & gunicorn -b 0.0.0.0:5000 --name server server.wsgi:app"

### MySQL
- mysql -uroot -padops2023 --ssl-mode=DISABLED -P3306 -h127.0.0.1

### Kylin
- Kylin Web UI: http://127.0.0.1:7070/kylin/query
  - user: ADMIN
  - psd: KYLIN
- Hdfs NameNode Web UI: http://127.0.0.1:50070
- Yarn ResourceManager Web UI: http://127.0.0.1:8088

### Jupyterlab
- docker logs opmldb | grep http://127.0.0.1:8888/lab

## Stop Services
- docker-compose -f docker-compose.yml down

## kafka
