#!/bin/bash

# wget https://github.com/polralimsu/dotori-world/raw/refs/heads/master/launch.sh
# sudo -u ec2-user bash $PWD/launch.sh

# rm */migrations/0*_*.py

cd $HOME
sudo dnf install -y git python3.14-devel mariadb114-devel gcc
git clone https://github.com/polralimsu/dotori-world.git
cd dotori-world
python3.14 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

#TOSS_CLIENT_KEY
#TOSS_SECRET_KEY
#TOSS_SECURITY_KEY
#DJANGO_SECRET_KEY <- python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
#DB_USER
#DB_PASSWORD
#AWS_STORAGE_BUCKET_NAME
#AWS_S3_CUSTOM_DOMAIN
#MY_DOMAIN

# use parameter store
echo "DB_HOST=$(aws secretsmanager get-secret-value --secret-id dotori-idc-db-host --output text --query SecretString --region ap-northeast-2)" >> .env
IFS= aws secretsmanager get-secret-value --secret-id dotori-secrets-2 --output text --query SecretString --region ap-northeast-2 | jq -r 'to_entries[] | "\(.key) \(.value)"' | while read -r key value; do echo "$key=\"$value\"" >> .env; done
source .env

cat >> .env <<EOF
DEBUG=False
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=https://${MY_DOMAIN},https://*.${MY_DOMAIN}
DATABASE_URL=mysql://$DB_USER:$DB_PASSWORD@$DB_HOST:3306/dotori_db
AWS_S3_REGION_NAME=ap-northeast-2
EMAIL_BACKEND=django_ses.SESBackend
DEFAULT_FROM_EMAIL=admin@$MY_DOMAIN
AWS_SES_REGION_NAME=ap-northeast-2
EOF

chmod 700 .env

COMMIT_HEAD=$(git rev-parse HEAD)

python create_translations.py

python manage.py shell << EOF
from django.core.management import call_command
from django.db import connection

upd = True

with connection.cursor() as cursor:
    cursor.execute("CREATE TABLE IF NOT EXISTS mg_lock(id CHAR(40) PRIMARY KEY)")
    cursor.execute("LOCK TABLE mg_lock WRITE")
    try:
        cursor.execute("SELECT id FROM mg_lock WHERE id = \"$COMMIT_HEAD\"")
        rows = [row[0] for row in cursor.fetchall()]
        upd = "$COMMIT_HEAD" not in rows
        cursor.execute("DELETE FROM mg_lock")
        cursor.execute("INSERT INTO mg_lock VALUES (\"$COMMIT_HEAD\")")
    finally:
        cursor.execute("UNLOCK TABLES")

if upd:
    call_command('migrate')
    call_command('collectstatic', '--no-input')
    print('migration done')
else:
    print('no migration')

EOF

pip install gunicorn

cat <<EOF | sudo tee /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon for Django Project
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=$PWD
ExecStart=$PWD/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind 0.0.0.0:8000 \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
