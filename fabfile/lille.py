import pydiploy
from fabric.api import env, execute, roles, task


@roles(['web', 'lb'])
def build_env():
    execute(pydiploy.prepare.build_env)


@task
def preprod_lille():
    """Define preprod stage."""
    env.roledefs = {
        'web': ['saas-lille-plana-pprd-1.srv.unistra.fr', 'saas-lille-plana-pprd-2.srv.unistra.fr'],
        'lb': ['saas-lille-plana-pprd-1.srv.unistra.fr', 'saas-lille-plana-pprd-2.srv.unistra.fr'],
    }
    # env.user = 'root'  # user for ssh
    env.backends = env.roledefs['web']
    env.server_name = 'TODO_DOMAIN_NAME'
    env.short_server_name = 'plana-api-pprd'
    env.static_folder = '/site_media/'
    env.server_ip = '130.79.245.212'
    env.no_shared_sessions = False
    env.server_ssl_on = True
    env.path_to_cert = '/etc/ssl/certs/mega_wildcard.pem'
    env.path_to_cert_key = '/etc/ssl/private/mega_wildcard.key'
    env.goal = 'preprod'
    env.socket_port = '8002'
    env.map_settings = {
        'accounts_api_spore_base_url': 'ACCOUNTS_API_CONF["BASE_URL"]',
        'accounts_api_spore_description_file': 'ACCOUNTS_API_CONF["DESCRIPTION_FILE"]',
        'accounts_api_spore_token': 'ACCOUNTS_API_CONF["TOKEN"]',
        'default_db_host': 'DATABASES["default"]["HOST"]',
        'default_db_name': 'DATABASES["default"]["NAME"]',
        'default_db_password': 'DATABASES["default"]["PASSWORD"]',
        'default_db_user': 'DATABASES["default"]["USER"]',
        'email_host': 'EMAIL_HOST',
        'email_host_password': 'EMAIL_HOST_PASSWORD',
        'email_host_user': 'EMAIL_HOST_USER',
        'email_port': 'EMAIL_PORT',
        'email_use_tls': 'EMAIL_USE_TLS',
        's3_access_key': 'AWS_ACCESS_KEY_ID',
        's3_bucket': 'AWS_STORAGE_BUCKET_NAME',
        's3_endpoint': 'AWS_S3_ENDPOINT_URL',
        's3_secret_key': 'AWS_SECRET_ACCESS_KEY',
        'secret_key': 'SECRET_KEY',
    }
    execute(build_env)


@task
def prod_lille():
    """Define prod stage."""
    env.roledefs = {
        'web': ['saas-lille-plana-prod-1.srv.unistra.fr', 'saas-lille-plana-prod-2.srv.unistra.fr'],
        'lb': ['saas-lille-plana-prod-1.srv.unistra.fr', 'saas-lille-plana-prod-2.srv.unistra.fr'],
    }
    # env.user = 'root'  # user for ssh
    env.backends = env.roledefs['web']
    env.server_name = 'TODO_DOMAIN_NAME'
    env.short_server_name = 'plana-api'
    env.static_folder = '/site_media/'
    env.server_ip = '130.79.245.214'
    env.no_shared_sessions = False
    env.server_ssl_on = True
    env.path_to_cert = '/etc/ssl/certs/mega_wildcard.pem'
    env.path_to_cert_key = '/etc/ssl/private/mega_wildcard.key'
    env.goal = 'prod'
    env.socket_port = '8002'
    env.map_settings = {
        'accounts_api_spore_base_url': 'ACCOUNTS_API_CONF["BASE_URL"]',
        'accounts_api_spore_description_file': 'ACCOUNTS_API_CONF["DESCRIPTION_FILE"]',
        'accounts_api_spore_token': 'ACCOUNTS_API_CONF["TOKEN"]',
        'default_db_host': 'DATABASES["default"]["HOST"]',
        'default_db_name': 'DATABASES["default"]["NAME"]',
        'default_db_password': 'DATABASES["default"]["PASSWORD"]',
        'default_db_user': 'DATABASES["default"]["USER"]',
        'email_host': 'EMAIL_HOST',
        'email_host_password': 'EMAIL_HOST_PASSWORD',
        'email_host_user': 'EMAIL_HOST_USER',
        'email_port': 'EMAIL_PORT',
        'email_use_tls': 'EMAIL_USE_TLS',
        's3_access_key': 'AWS_ACCESS_KEY_ID',
        's3_bucket': 'AWS_STORAGE_BUCKET_NAME',
        's3_endpoint': 'AWS_S3_ENDPOINT_URL',
        's3_secret_key': 'AWS_SECRET_ACCESS_KEY',
        'secret_key': 'SECRET_KEY',
    }
    execute(build_env)
