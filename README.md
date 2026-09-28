# RPAVS ERPNext Portal Guard

Frappe app that keeps RPA app users out of the ERPNext desk/portal and sends them to
https://app.rpavirtualstaffing.com. The only ERPNext pages they can still open are
`/login`, the OAuth2 authorize flow (so "Sign in" from the app keeps working) and
`/helpdesk/*` (including the API calls the Helpdesk pages make).

## Install (self-hosted bench)

    cd frappe-bench
    bench get-app /path/to/rpavs_erpnext_portal_guard     # or a git URL
    bench --site erp.rpa-hub.com install-app rpavs_erpnext_portal_guard
    bench restart

## Exempting users

Users who skip the redirect:
- `Administrator`
- users with the **ERP Portal Access** role (created on install) or **System Manager**
- emails listed in `rpa_portal_bypass_users` in site_config.json

## site_config.json options

    "rpa_portal_guard_enabled": 0,          // emergency off switch
    "rpa_app_url": "https://app.rpavirtualstaffing.com",
    "rpa_portal_bypass_roles": ["ERP Portal Access", "System Manager"],
    "rpa_portal_bypass_users": ["someone@rpapm.com"],
    "rpa_portal_allowed_sections": ["/helpdesk"]

## Recommended

In the OAuth Client used by the app, turn on **Skip Authorization**. That way users never
see the ERPNext consent screen.
