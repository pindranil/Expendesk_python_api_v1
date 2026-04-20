class InvoicePrompts:

    @staticmethod
    def get_language_instruction():
        return (
            "LANGUAGE HANDLING:\n"
            "- Translate all non-English text (merchant names, items, addresses, etc.) to English\n"
            "- Use accepted English names for places (e.g., Mumbai, not Bombai)\n"
            "- Preserve formatting of numbers, dates, invoice numbers, and GST numbers\n"
            "- Translate: Chinese (e.g., 白酒 → White Wine), Japanese (hiragana/kanji), Korean (hangul)\n"
        )

    @staticmethod
    def get_currency_rules():
        return (
            "CURRENCY RULES:\n"
            "- ₹ = INR, $ = USD, € = EUR, £ = GBP, Rp = IDR\n"
            "- If not shown, assume INR\n"
        )

    @staticmethod
    def get_formatting_rules():
        return (
            "FORMATTING:\n"
            "- Dates: YYYY-MM-DD\n"
            "- Amounts: exact decimal precision, no commas\n"
            "- All text: translated to English\n"
        )

    @staticmethod
    def get_shared_extraction_rules():
        return (
            "SHARED EXTRACTION RULES:\n"
            "1. Translate all text to English\n"
            "2. Read tax values exactly as shown. DO NOT infer or calculate CGST/SGST based on percentages or taxable value. Always prefer Tax Summary table values.\n"
            "3. Use Tax Summary sections for sgst_amount and cgst_amount fields\n"
            "4. If a field is not present in the invoice, return an empty string\n"
        )

    @staticmethod
    def get_translation_examples():
        return (
            "TRANSLATION EXAMPLES:\n"
            "- Hindi: 'होटल ताज' → 'Hotel Taj'\n"
            "- Bengali: 'মাছের ঝোল' → 'Fish Curry'\n"
            "- Chinese: '白酒' → 'White Wine'\n"
        )

    @staticmethod
    def get_combined_prompt():
        return (
            "You are an invoice data extraction specialist.\n"
            "Analyze this invoice image and do TWO things in one pass:\n"
            "  1. Classify the invoice type\n"
            "  2. Extract all structured data\n\n"

            # --- Shared rules ---
            # f"{InvoicePrompts.get_language_instruction()}"
            # f"{InvoicePrompts.get_currency_rules()}"
            f"{InvoicePrompts.get_formatting_rules()}"
            f"{InvoicePrompts.get_shared_extraction_rules()}\n"

            # --- Classification ---
            "CLASSIFICATION RULES:\n"
            "- Hotel: Room charges, accommodation fees\n"
            "- Food: Restaurant bills, in-room dining, bar, alcohol\n"
            "- Travel: Cab/train/flight tickets\n"
            "- Others: All other types\n"
            "- Priority order if mixed: Food > Hotel > Travel > Others\n\n"
            "Set `invoice_type` and the `type` field inside `data` to the same value: hotel, travel, food, or others.\n\n"

            # --- Hotel ---
            "IF HOTEL INVOICE:\n"
            "Set `type` to exactly: hotel\n"
            "Extract: merchant_name, invoice_no, total_amount_base, currency_code, invoice_date,\n"
            "         sgst_amount, cgst_amount, guest_company_name, guest_company_gst_no, guest_name,\n"
            "         check_in_date, check_out_date, total_days_stayed, state, city, pincode\n\n"
            "HOTEL SERVICE BREAKAGE (`hotel_service_breakage`) INSTRUCTIONS:\n"
            "- Extract each individual service line-item from the 'Voucher / Service Breakage' table exactly as-is\n"
            "- Maintain exact order as they appear — do NOT merge, group, or summarize\n"
            "- Extract even if date, description, SAC code, or amounts repeat across lines\n"
            "- Each item must contain:\n"
            "    * item_date\n"
            "    * description\n"
            "    * bill_type (accommodation / food / laundry / spa / transport / others)\n"
            "    * amount\n"
            "    * sac_code\n"
            "    * sgst_amount\n"
            "    * cgst_amount\n"
            "- EXCLUDE standalone tax lines: 'State GST', 'Central GST', 'SGST', 'CGST', 'IGST'\n"
            "- EXCLUDE summary lines: 'Day Total', 'Grand Total', 'Round Off'\n"
            "- EXCLUDE payment lines: 'Advance', 'Settlement Details'\n"
            "- If sgst_amount/cgst_amount not shown per line, compute from SAC code:\n"
            "    * SAC 996311 → SGST 6%, CGST 6%\n"
            "    * SAC 996331 or 996332 → SGST 9%, CGST 9%\n"
            "- Sum of SGST and CGST across all items must match the invoice Tax Summary\n"
            "- Never skip, reorder, or deduplicate any line-item\n"
            "- Do NOT round off or alter decimal places\n\n"

            # --- Travel ---
            "IF TRAVEL INVOICE:\n"
            "Set `type` to exactly: travel\n"
            "Extract: merchant_name, invoice_no, total_amount_base, currency_code, invoice_date,\n"
            "         sgst_amount, cgst_amount\n"
            "         mode_of_travel (flight/train/cab)\n"
            "         travel_class (Economy/Business/Sleeper/AC etc.)\n"
            "         from_location, to_location\n"
            "         departure_date, departure_time, arrival_date, arrival_time\n"
            "         distance (in km if shown, else empty string)\n"
            "         intra_inter_city ('intra' if same city, 'inter' if different cities)\n"
            "         liquor_items: empty list unless liquor explicitly present\n\n"

            # --- Food ---
            "IF FOOD INVOICE:\n"
            "Set `type` to exactly: food\n"
            "Extract: merchant_name, invoice_no, total_amount_base, currency_code, invoice_date,\n"
            "         sgst_amount, cgst_amount\n"

            "TOTAL AMOUNT EXTRACTION RULE (VERY IMPORTANT):\n"
            "- ALWAYS extract the FINAL PAYABLE AMOUNT\n"
            "- Prefer labels: 'Grand Total', 'Total Amount', 'Amount Payable', 'Net Total'\n"
            "- INCLUDE all taxes and rounding\n"
            "- DO NOT extract 'Sub Total', 'Item Total', or pre-tax amounts\n"
            "- If multiple totals exist, ALWAYS choose the LAST and FINAL amount printed on the bill\n"
            "- If 'Grand Total' exists, it MUST be used\n\n"

            "         liquor_items: list of alcoholic beverages only (description + amount)\n"
            "         If no liquor present, return empty list\n\n"

            # --- Others ---
            "IF OTHERS INVOICE:\n"
            "Set `type` to exactly: others\n"
            "Extract: merchant_name, invoice_no, total_amount_base, currency_code, invoice_date,\n"
            "         sgst_amount, cgst_amount\n"
            "         state, city, pincode (of merchant if shown, else empty string)\n"
            "         liquor_items: list of alcoholic beverages only (description + amount)\n"
            "         If no liquor present, return empty list\n\n"

            f"{InvoicePrompts.get_translation_examples()}"
        )