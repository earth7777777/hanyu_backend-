import frappe
from frappe.model.document import Document

@frappe.whitelist(allow_guest=True, methods=['POST'])
def create_rm_inbound_draft_from_receipt(overrides=None):
    if not overrides:
        frappe.throw(_('No data provided'))
    
    # 如果 receipt_photo 为空，必须填写 exception_reason
    if 'receipt_photo' not in overrides or not overrides['receipt_photo']:
        if 'exception_reason' not in overrides or not overrides['exception_reason']:
            frappe.throw(_('exception_reason is required when receipt_photo is empty'))
    
    return {'ok': True, 'data': overrides}
