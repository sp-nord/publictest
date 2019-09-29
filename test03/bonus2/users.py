import string
import random
import psycopg2
import fire
import settings


wp_dbname = settings.DB_NAME
wp_dbuser = settings.DB_USER
wp_dbpass = settings.DB_PASS
wp_dbhost = settings.DB_HOST if hasattr(settings, 'DB_HOST') else 'localhost'
wp_dbport = settings.DB_PORT if hasattr(settings, 'DB_PORT') else 5432
wp_prefix = settings.DB_PREFIX if hasattr(settings, 'DB_PREFIX') else 'wp_'

roles = {
    # 'administrator': 10,
    'editor': 7,
    'author': 2,
    'contributor': 1,
    'subscriber': 0
}
domain = '@mail.loc'
description = 'generated'
default_pass = 'Password@1'


def gen_user() -> str:
    """
    Generates user name
    :return: str in format "Firstname Lastname"
    """
    firstname = ''.join(random.sample(string.ascii_letters, random.randint(5, 8))).capitalize()
    lastname = ''.join(random.sample(string.ascii_letters, random.randint(5, 8))).capitalize()
    return '{} {}'.format(firstname, lastname)


def gen_user_list(lcount: int = 250) -> set:
    """
    Generates unique user names
    :param count: int. Amount of users needed
    :return: set of users
    """
    userlist = set()
    while len(userlist) < lcount:
        userlist.add(gen_user())
    return userlist


def gen_user_info(luser: str, lpass: str = default_pass, ldomain: str = domain, ldesc: str = description) -> dict:
    """
    Generates user info to be inserted into db
    :param luser: str. User name in format "Firstname Lastname"
    :param lpass: str. User password
    :param ldomain: str. Domain for user email
    :param ldesc: sr. Description for user
    :return: dict of user parametres
    """
    role = random.choice(list(roles.keys()))
    return {
        'username': luser.replace(' ', '.'),
        'nicename': luser.replace(' ', '-'),
        'email': luser.replace(' ', '.') + ldomain,
        'password': lpass,
        'capabilities': 'a:1:{{s:{}:"{}";b:1;}}'.format(len(role), role),
        'level': roles[role],
        'description': ldesc
    }


def users_to_db(lcount: int = 250) -> None:
    """
    Adds users to database
    :param lcount: int. Amount of users to add
    :return: nothing
    """
    conn = psycopg2.connect(dbname=wp_dbname, user=wp_dbuser, password=wp_dbpass, host=wp_dbhost, port=wp_dbport)
    cur = conn.cursor()

    for user in gen_user_list(lcount):
        user_info = gen_user_info(user)
        print('Adding {} with {}'.format(user_info['username'], user_info['capabilities']))
        cur.execute("insert into {}users (user_login, user_pass, user_email, user_nicename, display_name) \
                                  values (%(login)s, MD5(%(pass)s), %(mail)s, %(nice)s, %(login)s)".format(wp_prefix),
                    {'pref': wp_prefix,
                     'login': user_info['username'],
                     'pass': user_info['password'],
                     'mail': user_info['email'],
                     'nice': user_info['nicename']})
        cur.execute("select last_value from {}users_seq".format(wp_prefix))
        user_id = cur.fetchone()[0]
        cur.execute("insert into {}usermeta (user_id, meta_key, meta_value) \
                                     values (%(id)s, %(key)s, %(lvl)s)".format(wp_prefix),
                    {'id': user_id,
                     'key': '{}user_level'.format(wp_prefix),
                     'lvl': user_info['level']})
        cur.execute("insert into {}usermeta (user_id, meta_key, meta_value) \
                                     values (%(id)s, %(key)s, %(caps)s)".format(wp_prefix),
                    {'id': user_id,
                     'key': '{}capabilities'.format(wp_prefix),
                     'caps': user_info['capabilities']})
        conn.commit()

    cur.close()
    conn.close()


if __name__ == '__main__':
    fire.Fire(users_to_db)
