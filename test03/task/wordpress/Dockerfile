FROM wordpress:5.2.3-php7.3-fpm-alpine

ENV REDIS_PLUGIN_VERSION 1.4.3

RUN set -ex \
&& apk add --update --no-cache --virtual .deps \
    git \
    postgresql-dev \
    $PHPIZE_DEPS \
&& pecl install redis \
&& docker-php-ext-enable redis \
&& docker-php-ext-install pgsql \
&& docker-php-ext-enable pgsql \
&& cd /tmp \
&& git clone https://github.com/php4dev/heroku-wordpress.git \
&& cp -r ./heroku-wordpress/wp-content/pg4wp/ /usr/src/wordpress/wp-content/ \
&& cp ./heroku-wordpress/wp-content/pg4wp/db.php /usr/src/wordpress/wp-content/ \
&& curl -o ./redis-plugin.zip -fSL "https://downloads.wordpress.org/plugin/redis-cache.${REDIS_PLUGIN_VERSION}.zip" \
&& unzip ./redis-plugin.zip -d /usr/src/wordpress/wp-content/plugins/ \
&& rundeps="$(\
  scanelf --needed --nobanner --format '%n#p' --recursive /usr/local \
  | tr ',' '\n' \
  | sort -u \
  | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }' \
  )" \
&& apk add --no-cache --virtual .run-deps $rundeps \
&& rm ./redis-plugin.zip \
&& rm -rf ./heroku-wordpress \
&& apk del .deps \
&& cd /var/www/html

ADD ./docker-entrypoint-pg.sh /usr/local/bin/

ENTRYPOINT ["docker-entrypoint-pg.sh"]
CMD ["php-fpm"]
