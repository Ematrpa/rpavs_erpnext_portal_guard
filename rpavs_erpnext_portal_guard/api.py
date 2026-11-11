from urllib.parse import urlparse

import frappe
from werkzeug.utils import redirect

from rpavs_erpnext_portal_guard.guard import DEFAULT_APP_URL


@frappe.whitelist(allow_guest=True, methods=["GET"])
def logout(redirect_to=None):
    """
    End this browser's ERPNext session and send the user back to the RPA app's
    sign-in page. The RPA app navigates the browser here when the user logs out
    or must sign in with another account (Switch account), so the next sign-in
    asks for ERPNext credentials again instead of silently reusing the old
    session.

    It must be a top-level GET navigation: the `sid` cookie is SameSite=Lax, so
    a cross-site POST or fetch from the RPA app would not carry it.

    `redirect_to` (optional) is honoured only when its origin is the app URL or
    one listed in site_config `rpa_app_extra_urls` (e.g. a local dev frontend),
    so this endpoint can't be used as an open redirect.
    """
    if frappe.session.user != "Guest":
        frappe.local.login_manager.logout()

    app_url = (frappe.conf.get("rpa_app_url") or DEFAULT_APP_URL).rstrip("/")
    target = f"{app_url}/sign-in"

    if redirect_to:
        allowed = {_origin(u) for u in [app_url, *(frappe.conf.get("rpa_app_extra_urls") or [])]}
        origin = _origin(redirect_to)
        if origin and origin in allowed:
            target = redirect_to

    return redirect(target, code=302)


def _origin(url: str) -> str:
    parsed = urlparse(url or "")
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}".lower()
