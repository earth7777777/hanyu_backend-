import frappe

@frappe.whitelist(allow_guest=True, methods=["POST"])
def process_receipt_photo(receipt_photo=None, exception_reason=None):
    """
    视觉处理（阶段四最小可用版）：
    - 输入：receipt_photo（文件路径或文件标识）或 exception_reason
    - 输出：稳定 JSON（先占位，后续接入真实 OCR/VL）
    规则：不传 receipt_photo 时，必须填写 exception_reason
    """
    receipt_photo = (receipt_photo or "").strip() if isinstance(receipt_photo, str) else receipt_photo
    exception_reason = (exception_reason or "").strip() if isinstance(exception_reason, str) else exception_reason

    if not receipt_photo and not exception_reason:
        return {"ok": False, "error": "receipt_photo 为空时，必须填写 exception_reason"}

    # 阶段四：预埋键位（识别不到就给 None，不允许瞎编）
    result = {
        "ok": True,
        "source": "placeholder",
        "receipt_photo": receipt_photo,
        "exception_reason": exception_reason,
        # 主字段（后续由真实视觉模型填充）
        "invoice_no": None,
        "supplier": None,
        "net_weight_tons": None,
        "package_quantity": None,
        # 预埋键：打码扫码/回料
        "batch_no": None,
        "external_bag_code": None,
        "external_bag_code_list": None,
        "material_source_type": None,   # "new_material" / "regrind"
        "regrind_class": None,          # "direct_reuse" / "need_reprocessing" / "discard"
        # 备注/提示（给前端或AI触手做人审）
        "notes": []
    }
    return result
