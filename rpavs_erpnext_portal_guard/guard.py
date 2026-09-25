"""
Keep RPA app users out of the ERPNext desk/portal.

Users who log in to ERPNext with a browser session (cookie) may only reach the
login page and the OAuth2 authorize flow. Every other page redirects to the RPA
app, and every other API call made with the session cookie gets a 403.

The RPA backend proxy is not affected: it calls ERPNext with
`Authorization: Bearer <token>`, which carries no session cookie, so at
before_request time the session user is Guest and the request passes through.

Exempt users (can use ERPNext normally):
  - Administrator
  - anyone with one of the bypass roles (default: "ERP Portal Access", "System Manager")
  - anyone listed in site_config `rpa_portal_bypass_users`

site_config.json options (all optional):
  "rpa_portal_guard_enabled": 0                 -> turn the guard off
  "rpa_app_url": "https://app.rpavirtualstaffing.com"
  "rpa_portal_bypass_roles": ["ERP Portal Access", "System Manager"]
  "rpa_portal_bypass_users": ["someone@rpapm.com"]
"""

import frappe
from werkzeug.exceptions import Forbidden, abort
from werkzeug.utils import redirect

DEFAULT_APP_URL = "https://app.rpavirtualstaffing.com"
DEFAULT_BYPASS_ROLE = "ERP Portal Access"
DEFAULT_BYPASS_ROLES = [DEFAULT_BYPASS_ROLE, "System Manager"]

# Pages a blocked user may still open (needed for sign-in from the app).
ALLOWED_PAGE_PATHS = {"/login"}

# Static files the login / OAuth pages need.
ALLOWED_PREFIXES = ("/assets/", "/files/")

# API methods a blocked user may call with the session cookie.
ALLOWED_METHOD_PREFIXES = (
    "login",
    "logout",
    "frappe.integrations.oauth2.",  # authorize, approve, get_token, openid_profile...
    "frappe.www.login.",
    "frappe.auth.get_logged_user",
)


def enforce():
    if not frappe.conf.get("rpa_portal_guard_enabled", 1):
        return

    request = getattr(frappe.local, "request", None)
    if request is None or request.method == "OPTIONS":
        return

    user = getattr(getattr(frappe.local, "session", None), "user", None) or "Guest"
    if user == "Guest" or _is_exempt(user):
        return

    path = request.path.rstrip("/") or "/"
    if _is_allowed(path):
        return

    if path.startswith("/api/") or _is_ajax(request):
        raise Forbidden("ERPNext access is disabled for this user.")

    abort(redirect(frappe.conf.get("rpa_app_url") or DEFAULT_APP_URL, code=302))


def _is_exempt(user: str) -> bool:
    if user == "Administrator":
        return True
    if user in (frappe.conf.get("rpa_portal_bypass_users") or []):
        return True
    bypass_roles = frappe.conf.get("rpa_portal_bypass_roles") or DEFAULT_BYPASS_ROLES
    return bool(set(bypass_roles) & set(frappe.get_roles(user)))


def _is_allowed(path: str) -> bool:
    if path in ALLOWED_PAGE_PATHS or path.startswith(ALLOWED_PREFIXES):
        return True
    if path.startswith("/api/method/"):
        method = path[len("/api/method/") :]
        return method.startswith(ALLOWED_METHOD_PREFIXES)
    return False


def _is_ajax(request) -> bool:
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or "application/json" in (request.headers.get("Accept") or "")
    )
