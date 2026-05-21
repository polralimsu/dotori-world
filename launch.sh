#!/bin/bash
cd /root
sudo dnf install -y git python3.14-devel mariadb114-devel gcc
git clone https://github.com/polralimsu/dotori-world.git
cd dotori-world
python3.14 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

#TOSS_CLIENT_KEY
#TOSS_SECRET_KEY
#TOSS_SECURITY_KEY
#DJANGO_SECRET_KEY
#DB_USER
#DB_PASSWORD
#DB_HOST
#AWS_STORAGE_BUCKET_NAME
#AWS_S3_CUSTOM_DOMAIN
#MY_DOMAIN
IFS= aws secretsmanager get-secret-value --secret-id dotori-secrets --output text --query SecretString --region ap-northeast-2 | jq -r 'to_entries[] | "\(.key) \(.value)"' | while read -r key value; do echo "$key=\"$value\"" >> .env; done
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

python create_translations.py

if false; then
python manage.py migrate
python manage.py collectstatic --noinput
fi

pip install gunicorn

cat > /etc/systemd/system/gunicorn.service <<EOF
[Unit]
Description=gunicorn daemon for Django Project
After=network.target

[Service]
WorkingDirectory=/root/dotori-world
ExecStart=/root/dotori-world/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind 0.0.0.0:8000 \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gunicorn
systemctl start gunicorn