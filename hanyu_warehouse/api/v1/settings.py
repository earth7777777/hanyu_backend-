import frappe

@frappe.whitelist(allow_guest=True)
def get_rm_inbound_shadow_schema():
    """
    Shadow Schema API:
    从 Warehouse Settings.field_map 子表生成 RM Inbound 的“影子字段配置”，供前端/AI动态渲染。
    """
    doc = frappe.get_single("Warehouse Settings")

    # 总开关：enable_shadow_mapping 关闭时直接返回禁用标记
    if not getattr(doc, "enable_shadow_mapping", 0):
        return {"enabled": False, "doctype": "RM Inbound", "fields": []}

    fields = []
    for row in (doc.get("field_map") or []):
        fields.append({
            "target_field": row.target_field,
            "label_cn": row.label_cn,
            "fieldtype": row.fieldtype,
            "options": row.options,
            "required": int(row.required or 0),
        })

    return {"enabled": True, "doctype": "RM Inbound", "fields": fields}

@frappe.whitelist(allow_guest=True)
# DEBUG ONLY: keep for Stage4/5 troubleshooting; tighten auth before public deployment
def get_allow_ai_inbound():
    doc = frappe.get_single("Warehouse Settings")
    return {"allow_ai_inbound": int(getattr(doc, "allow_ai_inbound", 0))}
