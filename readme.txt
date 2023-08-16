#This project also requires the installation of REDIS & MAILHOG to function other than the dependencies mentioned in the requirements.txt
#This project also requires the running of REDIS, MAILHOG & CELERY in terminals other than `python3 app.py`

####MAILHOG####
<< install >>
sudo apt-get -y install golang-go
sudo apt-get install git
go install github.com/mailhog/MailHog@latest

<< run >>
~/go/bin/MailHog

####REDIS####
<< install >>
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make

make test

sudo cp src/redis-server /usr/local/bin/
sudo cp src/redis-cli /usr/local/bin/
rm -rf ../redis-stable *

<< run >>
cd redis-stable
redis-server ./redis.conf

####CELERY####
<< run >>
cd Desktop/testing/application
celery -A export worker --loglevel=INFO

cd Desktop/testing/application
celery -A batch:celery worker --beat --loglevel=info

>>All chron jobs are period adjusted. Since transactions begin from August, any demo before September needs to have the startDate &/or endDate modified aptly<<