import pydiploy
from fabric.api import env, execute, roles, task

env.csp_settings = {}
env.nginx_location_extra_directives = []

@roles(['web', 'lb'])
def build_env():
    execute(pydiploy.prepare.build_env)


@task
def preprod_rouen():
    """Define preprod stage."""
    env.roledefs = {
        'web': ['saas-rouen-plana-pprd-1.srv.unistra.fr', 'saas-rouen-plana-pprd-2.srv.unistra.fr'],
        'lb': ['rp-shib3-pprd-1.srv.unistra.fr', 'rp-shib3-pprd-2.srv.unistra.fr'],
    }
    # env.user = 'root'  # user for ssh
    env.application_name = 'api-rouen-pprd'
    env.backends = env.roledefs['web']
    env.server_name = 'TODO_DOMAIN_NAME'
    env.short_server_name = 'TODO_SHORT_SERVER_NAME'
    env.static_folder = '/site_media/'
    env.server_ip = '77.72.45.206'
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
        'association_default_amount_members_allowed': 'ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED',
        'association_is_site_default': 'ASSOCIATION_IS_SITE_DEFAULT',
        'cas_attribute_email': 'CAS_ATTRIBUTES_NAMES["email"]',
        'cas_attribute_first_name': 'CAS_ATTRIBUTES_NAMES["first_name"]',
        'cas_attribute_is_student': 'CAS_ATTRIBUTES_NAMES["is_student"]',
        'cas_attribute_last_name': 'CAS_ATTRIBUTES_NAMES["last_name"]',
        'cas_authorized_services': 'CAS_AUTHORIZED_SERVICES',
        'cas_name': 'CAS_NAME',
        'cas_server': 'CAS_SERVER',
        'cas_value_is_student': 'CAS_ATTRIBUTES_VALUES["is_student"]',
        'cas_version': 'CAS_VERSION',
        'default_db_host': 'DATABASES["default"]["HOST"]',
        'default_db_name': 'DATABASES["default"]["NAME"]',
        'default_db_password': 'DATABASES["default"]["PASSWORD"]',
        'default_db_user': 'DATABASES["default"]["USER"]',
        'default_from_email': 'DEFAULT_FROM_EMAIL',
        'email_host': 'EMAIL_HOST',
        'email_host_password': 'EMAIL_HOST_PASSWORD',
        'email_host_user': 'EMAIL_HOST_USER',
        'email_port': 'EMAIL_PORT',
        'email_template_frontend_url': 'EMAIL_TEMPLATE_FRONTEND_URL',
        'email_use_tls': 'EMAIL_USE_TLS',
        'ldap_enabled': 'LDAP_ENABLED',
        'migration_site_domain': 'MIGRATION_SITE_DOMAIN',
        'migration_site_name': 'MIGRATION_SITE_NAME',
        's3_access_key': 'AWS_ACCESS_KEY_ID',
        's3_bucket': 'AWS_STORAGE_BUCKET_NAME',
        's3_endpoint': 'AWS_S3_ENDPOINT_URL',
        's3_secret_key': 'AWS_SECRET_ACCESS_KEY',
        'secret_key': 'SECRET_KEY',
    }
    execute(build_env)


@task
def prod_rouen():
    """Define prod stage."""
    env.roledefs = {
        'web': ['saas-rouen-plana-prod-1.srv.unistra.fr', 'saas-rouen-plana-prod-2.srv.unistra.fr'],
        'lb': ['saas-rouen-plana-prod-1.srv.unistra.fr', 'saas-rouen-plana-prod-2.srv.unistra.fr'],
    }
    # env.user = 'root'  # user for ssh
    env.application_name = 'api-rouen-prod'
    env.backends = env.roledefs['web']
    env.server_name = 'TODO_DOMAIN_NAME'
    env.short_server_name = 'TODO_SHORT_SERVER_NAME'
    env.static_folder = '/site_media/'
    env.server_ip = '77.72.44.196'
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
        'association_default_amount_members_allowed': 'ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED',
        'association_is_site_default': 'ASSOCIATION_IS_SITE_DEFAULT',
        'cas_attribute_email': 'CAS_ATTRIBUTES_NAMES["email"]',
        'cas_attribute_first_name': 'CAS_ATTRIBUTES_NAMES["first_name"]',
        'cas_attribute_is_student': 'CAS_ATTRIBUTES_NAMES["is_student"]',
        'cas_attribute_last_name': 'CAS_ATTRIBUTES_NAMES["last_name"]',
        'cas_authorized_services': 'CAS_AUTHORIZED_SERVICES',
        'cas_name': 'CAS_NAME',
        'cas_server': 'CAS_SERVER',
        'cas_value_is_student': 'CAS_ATTRIBUTES_VALUES["is_student"]',
        'cas_version': 'CAS_VERSION',
        'default_db_host': 'DATABASES["default"]["HOST"]',
        'default_db_name': 'DATABASES["default"]["NAME"]',
        'default_db_password': 'DATABASES["default"]["PASSWORD"]',
        'default_db_user': 'DATABASES["default"]["USER"]',
        'default_from_email': 'DEFAULT_FROM_EMAIL',
        'email_host': 'EMAIL_HOST',
        'email_host_password': 'EMAIL_HOST_PASSWORD',
        'email_host_user': 'EMAIL_HOST_USER',
        'email_port': 'EMAIL_PORT',
        'email_template_frontend_url': 'EMAIL_TEMPLATE_FRONTEND_URL',
        'email_use_tls': 'EMAIL_USE_TLS',
        'ldap_enabled': 'LDAP_ENABLED',
        'migration_site_domain': 'MIGRATION_SITE_DOMAIN',
        'migration_site_name': 'MIGRATION_SITE_NAME',
        's3_access_key': 'AWS_ACCESS_KEY_ID',
        's3_bucket': 'AWS_STORAGE_BUCKET_NAME',
        's3_endpoint': 'AWS_S3_ENDPOINT_URL',
        's3_secret_key': 'AWS_SECRET_ACCESS_KEY',
        'secret_key': 'SECRET_KEY',
    }
    execute(build_env)
