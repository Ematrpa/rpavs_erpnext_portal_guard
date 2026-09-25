app_name = "rpavs_erpnext_portal_guard"
app_title = "RPAVS ERPNext Portal Guard"
app_publisher = "RPA"
app_description = "Blocks ERPNext desk/portal for app users and redirects them to the RPA app"
app_email = "emanuel@rpapm.com"
app_license = "MIT"

# Runs on every HTTP request, after the session cookie is resolved and
# before Frappe routes the request (desk, portal, /api, files...).
before_request = ["rpavs_erpnext_portal_guard.guard.enforce"]

after_install = "rpavs_erpnext_portal_guard.install.after_install"
