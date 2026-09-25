import frappe

from rpavs_erpnext_portal_guard.guard import DEFAULT_BYPASS_ROLE


def after_install():
    if not frappe.db.exists("Role", DEFAULT_BYPASS_ROLE):
        frappe.get_doc(
            {
                "doctype": "Role",
                "role_name": DEFAULT_BYPASS_ROLE,
                "desk_access": 1,
            }
        ).insert(ignore_permissions=True)
        frappe.db.commit()
