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
            "- Dates: YYYY-MM-DD format strictly — this applies to EVERY date field including "
            "item_date inside hotel_service_breakage line items\n"
            "- Examples of correct conversion: '25-Aug-23' → '2023-08-25', "
            "'23/06/23' → '2023-06-23', '24.06.2023' → '2023-06-24'\n"
            "- Amounts: exact decimal precision, no commas\n"
            "- All text: translated to English\n"
        )

    @staticmethod
    def get_shared_extraction_rules():
        return (
            "SHARED EXTRACTION RULES:\n"
            "1. Translate all text to English\n"
            "2. Read tax values exactly as shown. DO NOT infer or calculate CGST/SGST based on percentages "
            "or taxable value. Always prefer Tax Summary table values.\n"
            "3. Use Tax Summary sections for sgst_amount and cgst_amount fields\n"
            "4. If a field is not present in the invoice, return an empty string\n"
            "5. GST NUMBER EXTRACTION (CRITICAL):\n"
            "   - GST numbers are ALWAYS exactly 15 characters. Count them: if your result is not "
            "exactly 15 characters, you have made an error — go back and re-read.\n"
            "   - Structure: [2 digits][10 alphanumeric PAN][1 digit][1 letter][1 alphanumeric]\n"
            "   - Example: '20AAACC1645G1ZD' = 20 + AAACC1645G + 1 + Z + D = 15 chars ✓\n"
            "   - Read each character ONE BY ONE — do NOT compress, merge, or skip repeated characters\n"
            "   - Repeated characters like 'AAA' or 'CC' must be preserved exactly as printed\n"
            "   - Common OCR mistakes to AVOID:\n"
            "       * Collapsing 'AAA' → 'AA' (missing a repeated letter)\n"
            "       * Collapsing 'CC' → 'C' (missing a repeated letter)\n"
            "       * '0' vs 'O', '1' vs 'I', 'G' vs '6', 'S' vs '5', 'B' vs '8'\n"
            "   - After extracting, COUNT the characters. If not 15, re-read the GST number.\n"
            "   - guest_company_gst_no = GST number of the GUEST or CLIENT "
            "(labeled: Client GSTIN, Customer GSTIN, Buyer GSTIN, Party GSTIN)\n"
            "   - vendor_company_gst_no = GST number of the HOTEL or MERCHANT "
            "(labeled: GSTN, GSTIN, Hotel GSTIN, Our GSTIN — usually printed at top of invoice)\n"
            "   - These are TWO DIFFERENT numbers — never swap or copy one into the other\n"
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
    def build_expense_type_section(expense_types: list[dict]) -> str:
        """
        Builds the CLASSIFICATION RULES block dynamically from the expense_type_master list.

        expense_types example:
          [
            {"expense_type_id": 1,  "expense_type": "Hotel",       "eligibility_check_required": "Y"},
            {"expense_type_id": 2,  "expense_type": "Food",        "eligibility_check_required": "Y"},
            {"expense_type_id": 12, "expense_type": "Travel",      "eligibility_check_required": "Y"},
            ...
          ]

        The AI must set invoice_type to the EXACT expense_type string from this list.
        """
        if not expense_types:
            # Fallback to original hardcoded types if no list provided
            return (
                "CLASSIFICATION RULES:\n"
                "- Hotel: Room charges, accommodation fees\n"
                "- Food: Restaurant bills, in-room dining, bar, alcohol\n"
                "- Travel: Cab/train/flight tickets\n"
                "- Others: All other types\n"
                "- Priority order if mixed: Food > Hotel > Travel > Others\n\n"
                "Set `invoice_type` to one of: hotel, travel, food, others.\n\n"
            )

        # Build a numbered list of all types for the AI
        type_lines = "\n".join(
            f"  - {et['expense_type_id']}. {et['expense_type']}"
            for et in expense_types
        )

        # Build keyword hints for common types (helps the AI map correctly)
        keyword_hints = (
            "KEYWORD HINTS (use these to guide classification):\n"
            "- Hotel / Accommodation: room charges, room tariff, stay, check-in, check-out\n"
            "- Food: restaurant bill, dining, café, bar, meal, snack, beverage (non-hotel)\n"
            "- Travel / Conveyance: cab, taxi, auto, bus, train ticket, flight, boarding pass, Ola, Uber\n"
            "- Stationery: paper, pen, office supplies, printing material\n"
            "- Parking: parking fee, parking charge\n"
            "- Printing/Photocopying: print, photocopy, xerox\n"
            "- Software/Subscriptions: SaaS, app subscription, license, cloud service\n"
            "- Membership Fees: club, association, professional body\n"
            "- Training/Seminars: workshop, seminar, conference, course fee\n"
            "- Miscellaneous / Other: anything that does not clearly match the above\n"
        )

        return (
            "CLASSIFICATION RULES:\n"
            f"You must classify this invoice into EXACTLY ONE of the following expense types "
            f"from the company's expense master list:\n"
            f"{type_lines}\n\n"
            f"{keyword_hints}\n"
            "RULES:\n"
            "- Set `invoice_type` to the EXACT `expense_type` string from the list above "
            "(preserve original casing exactly as shown, e.g. 'Hotel', 'Food', 'Travel').\n"
            "- If the invoice clearly matches multiple types, use this priority: "
            "Food > Hotel > Travel > Conveyance > Others > Miscellaneous.\n"
            "- Never invent a type not in the list. If unsure, pick the closest match or "
            "the 'Miscellaneous' / 'Other' entry.\n\n"
        )

    @staticmethod
    def get_combined_prompt(expense_types: list[dict] | None = None) -> str:
        """
        Build the full extraction prompt.
        expense_types: list of dicts from expense_type_master (passed from Java via API).
        """
        if expense_types is None:
            expense_types = []

        classification_section = InvoicePrompts.build_expense_type_section(expense_types)

        # Determine which types map to hotel/food/travel for conditional extraction blocks
        # We normalise to lowercase for comparison
        type_names_lower = {et["expense_type"].lower() for et in expense_types}
        has_hotel    = any(t in type_names_lower for t in ("hotel", "accommodation"))
        has_travel   = any(t in type_names_lower for t in ("travel", "conveyance"))
        has_food     = "food" in type_names_lower

        return (
            "You are an invoice data extraction specialist.\n"
            "Analyze this invoice image and do TWO things in one pass:\n"
            "  1. Classify the invoice type\n"
            "  2. Extract all structured data\n\n"

            f"{InvoicePrompts.get_formatting_rules()}"
            f"{InvoicePrompts.get_shared_extraction_rules()}\n"

            f"{classification_section}"

            # ── Hotel block ────────────────────────────────────────
            + (
                "IF HOTEL / ACCOMMODATION INVOICE:\n"
                "Extract: merchant_name, invoice_no, total_amount,  invoice_date,\n"
                "         sgst_amount, cgst_amount, guest_company_name, guest_company_gst_no,\n"
                "         vendor_company_gst_no, guest_name,\n"
                "         check_in_date, check_out_date, total_days_stayed, state, city, pincode\n\n"

                "HOTEL SERVICE BREAKAGE (`service_breakage`) INSTRUCTIONS:\n"
                "- Extract each individual service line-item from the 'Voucher / Service Breakage' table exactly as-is\n"
                "- Maintain exact order as they appear — do NOT merge, group, or summarize\n"
                "- Extract even if date, description, SAC code, or amounts repeat across lines\n"
                "- Each item must contain:\n"
                "    * item_date — MUST be in YYYY-MM-DD format\n"
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
                if has_hotel else ""
            )

            # ── Travel block ───────────────────────────────────────
            + (
                "IF TRAVEL / CONVEYANCE INVOICE:\n"
                "Extract: merchant_name, invoice_no, total_amount,  invoice_date,\n"
                "         sgst_amount, cgst_amount\n"
                "         mode_of_travel (flight/train/cab)\n"
                "         travel_class (Economy/Business/Sleeper/AC etc.)\n"
                "         from_location, to_location\n"
                "         departure_date, departure_time, arrival_date, arrival_time\n"
                "         distance (in km if shown, else empty string)\n"
                "         intra_inter_city ('intra' if same city, 'inter' if different cities)\n\n"
                if has_travel else ""
            )

            # ── Food block ─────────────────────────────────────────
            + (
                "IF FOOD INVOICE:\n"
                "Extract: merchant_name, invoice_no, total_amount,  invoice_date,\n"
                "         sgst_amount, cgst_amount\n\n"
                if has_food else ""
            )

            # ── Total amount rule (always) ─────────────────────────
            + (
                "TOTAL AMOUNT EXTRACTION RULE (VERY IMPORTANT):\n"
                "- ALWAYS extract the FINAL PAYABLE AMOUNT\n"
                "- Prefer labels: 'Grand Total', 'Total Amount', 'Amount Payable', 'Net Total'\n"
                "- INCLUDE all taxes and rounding\n"
                "- DO NOT extract 'Sub Total', 'Item Total', or pre-tax amounts\n"
                "- If multiple totals exist, ALWAYS choose the LAST and FINAL amount printed on the bill\n"
                "- If 'Grand Total' exists, it MUST be used\n\n"
            )

            # ── Others block (always present as fallback) ──────────
            + (
                "FOR ALL OTHER INVOICE TYPES:\n"
                "Extract: merchant_name, invoice_no, total_amount,  invoice_date,\n"
                "         sgst_amount, cgst_amount\n"
                "         state, city, pincode (of merchant if shown, else empty string)\n\n"
            )

            + f"{InvoicePrompts.get_translation_examples()}"
        )