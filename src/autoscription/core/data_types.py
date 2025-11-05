pages_dtype = {
    "prescription_scanned_pages": "string",
    "pdf_file_name": "string",
    "coupons_found": "string",
    "file_path": "string",
    "coupons_required": "int8",
    "execution": "int8",
    "prescription": "string",
    "scan_last_three_digits": "string",
    "page": "int8",
    "pages": "int8",
    "category": "int8",
    "sign_found": "int8",
    "sign_required": "int8",
    "stamps_found": "int8",
    "stamps_required": "int8",
    "pharmacist_idika_prescription_full": "string",
    "type": "string",
    "first_execution": "boolean",
    "digital": "boolean",
    "unit": "string",
    "category_name": "string",
    "100%": "boolean",
    "sign_check": "boolean",
    "stamps_check": "boolean",
    "coupon_check": "boolean",
    "coupon_precheck": "boolean",
    "document_type": "string",
    "doc_name": "string",
    "patient_name": "string",
    "insurance_amount": "string",
    "patient_amount": "string",
    "missing_tapes": "string",
    "surplus_tapes": "string",
}

injection_pages_dtype = pages_dtype.copy()
injection_pages_dtype["pr_order_timestamp"] = "datetime64[ns]"
injection_pages_dtype.pop("prescription_scanned_pages")

dosages_dtype = {
    "boxes_required": "int8",
    "boxes_provided": "int8",
    "dosage_category": "string",
    "dosage_description": "string",
    "description": "string",
    "pills_required": "int16",
    "description_quantity": "int16",
    "dosage": "float32",
    "dosage_qnt": "int16",
    "dosage_repeat": "int8",
    "patient_part": "string",
    "unit_price": "float32",
    "patient_return": "float32",
    "total": "float32",
    "diff": "float32",
    "patient_contrib": "float32",
    "gov_contrib": "float32",
    "description_org": "string",
    "dosage_check": "string",
    "prescription": "string",
    "scan_last_three_digits": "int16",
    "boxes_provided": "int8",
    "boxes_provided_multiple_executions": "int8",
    "is_past_partial_exec": "boolean",
}

daily_pres_dtype = {
    "prescription": "string",
    "execution": "int8",
    "pr_order_timestamp": "datetime64[ns]",
}

index_dtype = {
    "id": "string",
    "prescription_scanned_pages": "string",
    "old_filname": "string",
    "stack_number": "int16",
}
