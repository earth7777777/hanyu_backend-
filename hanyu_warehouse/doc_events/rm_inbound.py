# apps/hanyu_warehouse/hanyu_warehouse/doc_events/rm_inbound.py

import frappe


def validate_rm_inbound(doc, method=None):
    """
    Hook: RM Inbound -> validate
    作用：
    1) 重量复核：按 (袋数 * 单袋重量kg) / 1000 => 吨，和实测吨数比对，偏差>1%就写备注预警
    2) 禁止混放：用 RM Inbound 的库位字段去查 Location Occupancy，若占用物料不同则阻断保存
    """

    _weight_audit(doc)
    _location_mix_lock(doc)


def _weight_audit(doc):
    # 字段约定（来自阶段一/阶段二对齐）
    material_name = doc.get("f01")  # 入库物料
    gross_tons = doc.get("f04")     # 实测毛重(吨)
    bag_count = doc.get("f05")      # 包数/袋数
    remark = doc.get("f11") or ""   # 备注说明

    # 必填字段缺失时，交给表单自己的必填校验；这里不重复抛错
    if not material_name or gross_tons is None or bag_count is None:
        return

    bag_weight_kg = _get_bag_weight_kg(material_name)
    expected_tons = (float(bag_count) * float(bag_weight_kg)) / 1000.0

    # 偏差阈值：1%
    if expected_tons <= 0:
        return

    diff_ratio = abs(float(gross_tons) - expected_tons) / expected_tons
    if diff_ratio > 0.01:
        warning = "[系统预警] 实收吨数与袋数换算偏差超过 1%"
        if warning not in remark:
            doc["f11"] = (remark + ("\n" if remark else "") + warning).strip()


def _get_bag_weight_kg(material_name: str) -> float:
    """
    取数优先级：
    1) Material.bag_weight_kg
    2) Warehouse Settings.default_bag_weight_kg
    3) 默认 25
    """
    # 1) Material
    bag_weight = frappe.db.get_value("Material", material_name, "bag_weight_kg")
    if bag_weight:
        return float(bag_weight)

    # 2) Warehouse Settings（取第一条）
    settings = frappe.db.get_value("Warehouse Settings", None, "default_bag_weight_kg")
    if settings:
        return float(settings)

    # 3) fallback
    return 25.0


def _location_mix_lock(doc):
    """
    禁止混放锁：
    - 用 RM Inbound 的库位字段（默认按 f08）去匹配 Location Occupancy.location_id
    - 若已有占用且 material != 本次 f01，则 frappe.throw 阻断
    """
    location_value = doc.get("f08")   # 库位/卸货位置（待您确认确实用于库位）
    material_name = doc.get("f01")

    if not location_value or not material_name:
        return

    occ = frappe.db.get_value(
        "Location Occupancy",
        {"location_id": location_value},
        ["name", "material"],
        as_dict=True,
    )

    if not occ:
        return

    occupied_material = occ.get("material")
    if occupied_material and occupied_material != material_name:
        frappe.throw("禁止混放：该库位已被其他物料占用")

