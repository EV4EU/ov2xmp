"""
Custom LDAP authentication backend for O-V2X-MP. 

1. **authenticate_ldap_user()** - Overrides the default authenticate_ldap_user() behaviour [[ldap.py#authenticate_ldap_user]]

"""


import re
from django.core.cache import cache
import ldap
from ldap import dn as dn_lib
from django_auth_ldap.backend import LDAPBackend, _LDAPUser
from ldap.ldapobject import LDAPObject
import settings
import os


class CustomLDAPBackend(LDAPBackend):

    # === authenticate_ldap_user ===

    """
    Purpose of this method is to override the default behaviour of `authenticate_ldap_user()`.
    According to the default behaviour, Django receives the username of the HTML login form and attempts bind operation as `CN=username,CN=Users,DC=trsc,DC=net` (if search DN is `CN=Users,DC=trsc,DC=net`). 
    However, this is not always correct, because the username is not always used as CN. For example, AD applies the full name as CN. </br>

    To overcome this, the custom authentication backend, first binds with the read-only user and searches for the LDAP user with the given username. 
    The username mapping (e.g., `uid` or `sAMAccountName`) is provided by the `AUTH_LDAP_SEARCH_ATTRIBUTE` environmental variable by the O-V2X-MP admin.
    Then, the method replaces the incorrect DN of the `ldap_user` received in `authenticate_ldap_user()` with the DN retrieved from the user's 
    LDAP object. Finally, Django sends the correct LDAP request including the correct DN. </br>
    **param** - *ldap_user* : The LDAP user object initially received by `authenticate_ldap_user()`. The DN attribute of this object will be replaced in order to ensure correct authentication. </br>
    **param** - *password* : The LDAP user password. </br>
    """
    def authenticate_ldap_user(self, ldap_user, password):
        # Splits the DN string of the user, in order to retrieve the username. The LDAP search will be performed based on the username.
        uid = ldap_user.dn.split(',')[0].split('=')[1]

        BIND_DN = os.environ.get('AUTH_LDAP_BIND_DN', None)
        BIND_PASSWORD = os.environ.get('AUTH_LDAP_BIND_PASSWORD', None)

        # Search filter will be something like `(sAMAccountName=username)`.
        search_filter = '(' + os.environ.get('AUTH_LDAP_SEARCH_ATTRIBUTE', 'None') + '=' + uid + ')'

        ldap_server = ldap.initialize(uri=os.environ.get('AUTH_LDAP_SERVER_URI', None))

        # This enables STARTTLS for LDAP connection, but deactivates certificate check, in case the certificate is self-signed 
        # (insecure, but common case for internal networks)
        ldap_server.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        ldap_server.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
        ldap_server.start_tls_s()
        ldap_server.simple_bind_s(BIND_DN, BIND_PASSWORD)

        result = ldap_server.search_s(os.environ.get('AUTH_LDAP_SEARCH_DN', None), ldap.SCOPE_SUBTREE, search_filter)

        ldap_server.unbind_s()

        for dn, entry in result:
            # Returned value of `repr()` is "`'CN=Full Name,CN=Users,DC=trsc,DC=net'`". We need to remove `'`.
            user_dn = repr(dn)    
            # Removes `'` before and after the string     
            user_dn = user_dn[1:-1]

            # Replaces DN
            ldap_user._user_dn = user_dn

            user = ldap_user.authenticate(password)
            return user
