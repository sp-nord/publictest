TIMEZONE="Asia/Jerusalem"
LOCALE="C.UTF-8"
SSH_PORT="2498"
SSH_CONF="/etc/ssh/sshd_config"

SERVICE_USER="serviceuser"
USER_SUDOERS="/etc/sudoers.d/$SERVICE_USER"

MONIT_CONF="/etc/monit/conf.d/httpd.conf"
NGINX_PATH="/etc/nginx"
NGINX_CONF="$NGINX_PATH/sites-available/monit.conf"


# Time zone
timedatectl set-timezone $TIMEZONE

# Locale
update-locale LANG=$LOCALE

# Move sshd to listen port 2498
if grep -e "^Port\s" $SSH_CONF
then
  sed -i "s/^Port\s.*/Port $SSH_PORT/" $SSH_CONF
else
  echo "Port $SSH_PORT" >> $SSH_CONF
fi

# Deny remote root
sed -i "s/\(^PermitRootLogin.*\)/#\1/g" $SSH_CONF

# Create serviceuser
useradd -s /usr/sbin/nologin $SERVICE_USER

# Serviceuser sudo stuff
touch $USER_SUDOERS
cat << EOF > $USER_SUDOERS
$SERVICE_USER ALL=(root) NOPASSWD: /bin/systemctl start*
$SERVICE_USER ALL=(root) NOPASSWD: /bin/systemctl stop*
$SERVICE_USER ALL=(root) NOPASSWD: /bin/systemctl restart*
EOF

# Install software
apt -y install nginx
apt -y install monit

# Configure monit
touch $MONIT_CONF
cat << EOF > $MONIT_CONF
set httpd
  port 12812
  use address localhost
  allow localhost
EOF

# Configure nginx
mkdir -p $NGINX_PATH/auth && touch $NGINX_PATH/auth/.htmonit
echo "monit:$(openssl passwd -apr1 tinom)" > $NGINX_PATH/auth/.htmonit

touch $NGINX_CONF
cat << EOF > $NGINX_CONF
server {
  listen 2812;
  location / {
    auth_basic "Welcome";
    auth_basic_user_file $NGINX_PATH/auth/.htmonit;
    proxy_pass http://127.0.0.1:12812;
  }
}
EOF

ln -s $NGINX_CONF $NGINX_PATH/sites-enabled/

# Restart stuff in the very end
systemctl restart monit \
&& systemctl restart nginx \
&& systemctl restart sshd
