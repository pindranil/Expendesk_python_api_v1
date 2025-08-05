# class InvoicePrompts:
    
#     @staticmethod
#     def get_language_instruction():
#         """Language handling instruction to be added to all prompts"""
#         return (
#             "LANGUAGE HANDLING:\n"
#             "- If the invoice is in any language other than English, translate ALL extracted information to English\n"
#             "- Convert merchant names, addresses, item descriptions, and service descriptions to English\n"
#             "- Keep numerical values, dates, and reference numbers unchanged\n"
#             "- For place names, use commonly accepted English names (e.g., Mumbai not Bombai)\n"
#             "- Preserve original formatting for invoice numbers, GST numbers, and other reference codes\n\n"
#         )
    
#     @staticmethod
#     def get_base_prompt():
#         """Base prompt to determine invoice type with language support"""
#         return (
#             "Analyze this invoice image and first determine the invoice type.\n"
#             "Classify as one of: hotel, travel, food, or other\n\n"
            
#             f"{InvoicePrompts.get_language_instruction()}"
            
#             "Look for key indicators:\n"
#             "- Hotel: Room charges, hotel name, check-in/check-out dates\n"
#             "- Travel: Flight tickets, train tickets, cab services, travel agencies\n"
#             "- Food: Restaurant bills, food delivery, catering services\n"
#             "- Other: All other types of invoices\n\n"
#             "Return only the classification: hotel, travel, food, or other"
#         )
    
#     @staticmethod
#     def get_hotel_prompt():
#         """Detailed prompt specifically for hotel invoices"""
#         return (
#             "This is a HOTEL INVOICE. Extract ALL information with EXACT precision.\n\n"
            
#             "CRITICAL EXTRACTION RULES:\n"
#             "1. Read ALL numbers with EXACT decimal precision as shown (e.g., 270.05 NOT 270.00)\n"
#             "2. Look at the main service items table AND the tax summary section\n"
#             "3. Extract SGST/CGST amounts from the 'Tax Summary' section - these are official amounts\n"
#             "4. For hotel_service_breakage: Include ONLY service items like Room Tariff, In-Room Dining, etc.\n"
#             "5. DO NOT include separate tax line items in service breakage\n"
#             "6. Match service items with their corresponding SAC codes and tax rates\n\n"
#             "5. Extract the currency if shown — use standard abbreviation:\n"
#                 "   - ₹ = INR\n"
#                 "   - $ = USD\n"
#                 "   - € = EUR\n"
#                 "   - £ = GBP\n"
#                 "   - If currency is not mentioned, default to 'INR'\n\n"
#             "7. Add a `type` field to each item in `hotel_service_breakage` to indicate the category of service:\n"
#                 "   - 'accommodation' for room tariff\n"
#                 "   - 'food' for in-room dining, restaurant services\n"
#                 "   - 'laundry', 'spa', 'transport' or other categories if mentioned\n\n"    
            
#             "CRITICAL TAX EXTRACTION - DO NOT CALCULATE, ONLY READ:\n"
#             "- NEVER calculate tax amounts by applying percentages to service amounts\n"
#             "- ALWAYS read tax amounts directly from the 'Tax Summary' section\n"
#             "- Look for patterns like 'Central GST @ 6.00%: 270.00' or 'State GST @ 9.00%: 130.05'\n"
#             "- Use the EXACT amounts shown after the colon, not calculated values\n"
#             "- Match each service to its tax rate (6% or 9%) and use corresponding amounts from summary\n\n"
            
#             "TAX MATCHING PROCESS FOR HOTELS:\n"
#             "1. Identify each service item (Room Tariff, In-Room Dining, etc.) and its tax rate\n"
#             "2. Find the matching tax rate lines in Tax Summary section\n"
#             "3. Extract exact amounts (e.g., 'State GST @ 9.00%: 130.05' → use 130.05)\n"
#             "4. Assign these exact amounts to corresponding service items\n"
#             "5. DO NOT multiply service amounts by tax percentages\n\n"
           
            
#             "EXAMPLE TAX MATCHING:\n"
#             "If Tax Summary shows:\n"
#             "- Central GST @ 6.00%: 270.00\n"
#             "- Central GST @ 9.00%: 130.05\n"
#             "- State GST @ 6.00%: 270.05\n"
#             "- State GST @ 9.00%: 130.05\n"
#             "Then assign 270.00/270.05 to 6% services and 130.05/130.05 to 9% services\n\n"
            
#             "FORMATTING:\n"
#             "- All dates in ISO format: YYYY-MM-DD\n"
#             "- All amounts as exact decimals (no commas, preserve precision)\n\n"
            
#             "Return complete hotel invoice data using Tax Summary amounts only."
#         )
    
#     @staticmethod
#     def get_travel_prompt():
#         """Detailed prompt specifically for travel invoices"""
#         return (
#             "This is a TRAVEL INVOICE. Extract ALL information with EXACT precision.\n\n"
            
#             "CRITICAL EXTRACTION RULES:\n"
#             "1. Read ALL numbers with EXACT decimal precision as shown\n"
#             "2. Look for travel-specific details like routes, dates, passenger info\n"
#             "3. Extract tax amounts from tax summary or breakdown sections\n"
#             "4. Include travel service details (flights, trains, cabs, etc.)\n\n"
#             "5. Extract the currency if shown — use standard abbreviation:\n"
#                 "   - ₹ = INR\n"
#                 "   - $ = USD\n"
#                 "   - € = EUR\n"
#                 "   - £ = GBP\n"
#                 "   - If currency is not mentioned, default to 'INR'\n\n"
            
#             "TRAVEL-SPECIFIC FIELDS TO EXTRACT:\n"
#             "- merchant_name, invoice_no, total_amount, invoice_date\n"
#             "- sgst_amount, cgst_amount, igst_amount (if applicable)\n"
#             "- company_name, gst_no, passenger_name\n"
#             "- travel_from, travel_to, travel_date\n"
#             "- travel_type (flight/train/cab/bus)\n"
#             "- ticket_number, seat_number, class_type\n"
#             "- travel_service_breakage with service details\n\n"
            
#             "FORMATTING:\n"
#             "- All dates in ISO format: YYYY-MM-DD\n"
#             "- All amounts as exact decimals\n\n"
            
#             "Return complete travel invoice data."
#         )
    
#     @staticmethod
#     def get_food_prompt():
#         """Detailed prompt specifically for food invoices with language support"""
#         return (
#             "This is a FOOD INVOICE. Extract ALL information with EXACT precision.\n\n"
            
#             f"{InvoicePrompts.get_language_instruction()}"
            
#             "CRITICAL EXTRACTION RULES:\n"
#             "1. Read ALL numbers with EXACT decimal precision as shown\n"
#             "2. Look for food items, quantities, and prices\n"
#             "3. Extract tax amounts from tax breakdown sections\n"
#             "4. Include food service details and item breakdowns\n"
#             "5. Extract the currency if shown — use standard abbreviation:\n"
#             "   - ₹ = INR\n"
#             "   - $ = USD\n"
#             "   - € = EUR\n"
#             "   - £ = GBP\n"
#             "   - If currency is not mentioned, default to 'INR'\n"
#             "6. Translate all food items and restaurant details to English\n\n"
            
#             "FOOD-SPECIFIC FIELDS TO EXTRACT:\n"
#             "- merchant_name: Look for restaurant name at top of receipt (translate if needed)\n"
#             "- invoice_no: Look for receipt number, order number, or bill number\n"
#             "- total_amount: Final total amount (应付金额, 合计, Total, etc.)\n"
#             "- invoice_date: Date from receipt header or timestamp\n"
#             "- sgst_amount, cgst_amount, service_charge: Extract if present\n"
#             "- company_name, gst_no, customer_name: Extract if available\n"
#             "- restaurant_name: Same as merchant_name unless different\n"
#             "- restaurant_address: Full address if shown\n"
#             "- table_number: Table number if mentioned\n"
#             "- order_type: dine-in/takeaway/delivery (infer from context)\n"
#             "- food_items_breakage: ALL items with quantities, unit prices, and total prices\n"
#             "- Include alcohol/beverage items separately if present\n"
#             "- Look for items in columns: item_name, quantity, unit_price, total_price\n\n"
            
#             "TRANSLATION EXAMPLES:\n"
#             "- Hindi: 'बटर चिकन' → 'Butter Chicken', 'नान' → 'Naan'\n"
#             "- Bengali: 'মাছের ঝোল' → 'Fish Curry', 'ভাত' → 'Rice'\n"
#             "- Chinese: '白酒' → 'White Wine/Liquor', '啤酒' → 'Beer', '红烧肉' → 'Braised Pork'\n"
#             "- Keep authentic dish names but add English descriptions where helpful\n"
#             "- For alcohol/liquor items, clearly identify the type (wine, beer, spirits, etc.)\n\n"
            
#             "FORMATTING:\n"
#             "- All dates in ISO format: YYYY-MM-DD\n"
#             "- All amounts as exact decimals\n"
#             "- All text fields in English\n\n"
            
#             "Return complete food invoice data with all information translated to English."
#         )
    
#     @staticmethod
#     def get_other_prompt():
#         """Generic prompt for other invoice types"""
#         return (
#             "This is a GENERAL INVOICE. Extract ALL information with EXACT precision.\n\n"
            
#             "CRITICAL EXTRACTION RULES:\n"
#             "1. Read ALL numbers with EXACT decimal precision as shown\n"
#             "2. Extract all visible tax information\n"
#             "3. Include service/product details as available\n\n"
            
#             "GENERAL FIELDS TO EXTRACT:\n"
#             "- merchant_name, invoice_no, total_amount, invoice_date\n"
#             "- sgst_amount, cgst_amount, igst_amount (if applicable)\n"
#             "- company_name, gst_no, customer_name\n"
#             "- service_description, items_breakage\n\n"
            
#             "FORMATTING:\n"
#             "- All dates in ISO format: YYYY-MM-DD\n"
#             "- All amounts as exact decimals\n\n"
            
#             "Return complete invoice data."
#         )
class InvoicePrompts:
    
    @staticmethod
    def get_language_instruction():
        """Language handling instruction to be added to all prompts"""
        return (
            "LANGUAGE HANDLING:\n"
            "- If the invoice is in any language other than English, translate ALL extracted information to English\n"
            "- Convert merchant names, addresses, item descriptions, and service descriptions to English\n"
            "- Keep numerical values, dates, and reference numbers unchanged\n"
            "- For place names, use commonly accepted English names (e.g., Mumbai not Bombai)\n"
            "- Preserve original formatting for invoice numbers, GST numbers, and other reference codes\n"
            "- For Chinese text: Translate characters to English (e.g., 白酒 → White Wine, 啤酒 → Beer)\n"
            "- For Japanese text: Translate hiragana/katakana/kanji to English\n"
            "- For Korean text: Translate hangul to English\n"
            "- Always provide English translations even if original language names are commonly used\n\n"
        )
    
    @staticmethod
    def get_base_prompt():
        """Base prompt to determine invoice type with language support"""
        return (
            "Analyze this invoice image and first determine the invoice type.\n"
            "Classify as one of: hotel, travel, food, or other\n\n"
            
            f"{InvoicePrompts.get_language_instruction()}"
            
            "Look for key indicators:\n"
            "- Hotel: Room charges, accommodation fees, check-in/check-out dates, room tariff\n"
            "  NOTE: Hotel restaurant/bar bills should be classified as 'food', not 'hotel'\n"
            "- Travel: Flight tickets, train tickets, cab services, travel agencies\n"
            "- Food: Restaurant bills, food delivery, catering services, bar bills, alcohol/liquor sales\n"
            "  INCLUDES: Hotel restaurant bills, room service food, bar tabs, even if from hotels\n"
            "- Other: All other types of invoices\n\n"
            
            "CLASSIFICATION PRIORITY:\n"
            "1. If invoice contains food/drink items or alcohol → classify as 'food'\n"
            "2. If invoice contains accommodation/room charges → classify as 'hotel'\n"
            "3. If invoice contains transport services → classify as 'travel'\n"
            "4. Everything else → classify as 'other'\n\n"
            "Return only the classification: hotel, travel, food, or other"
        )
    # @staticmethod
    # def get_hotel_prompt():
    #     """Detailed prompt specifically for hotel invoices with language support"""
    #     return (
    #         "This is a HOTEL INVOICE. Extract ALL information with EXACT precision.\n\n"
            
    #         f"{InvoicePrompts.get_language_instruction()}"
            
    #         "CRITICAL EXTRACTION RULES:\n"
    #         "1. Read ALL numbers with EXACT decimal precision as shown (e.g., 270.05 NOT 270.00)\n"
    #         "2. Look at the main service items table AND the tax summary section\n"
    #         "3. Extract SGST/CGST amounts from the 'Tax Summary' section — these are official amounts\n"
    #         "4. For `hotel_service_breakage`: Include ONLY service items like Room Tariff, In-Room Dining, etc.\n"
    #         "5. DO NOT include separate tax line items in service breakage (e.g., 'Central GST @ 6%')\n"
    #         "6. Match service items with their corresponding SAC codes and tax rates\n"
    #         "7. Extract the currency if shown — use standard abbreviation:\n"
    #         "   - ₹ = INR\n"
    #         "   - $ = USD\n"
    #         "   - € = EUR\n"
    #         "   - £ = GBP\n"
    #         "   - If currency is not mentioned, default to 'INR'\n"
    #         "8. For each item in `hotel_service_breakage`, include a `type` field:\n"
    #         "   - 'accommodation' for room tariff\n"
    #         "   - 'food' for in-room dining, restaurant services\n"
    #         "   - 'laundry', 'spa', 'transport' or other categories if mentioned\n"
    #         "9. DO NOT merge or combine multiple service rows — extract each row **exactly as it appears**, with separate tax assignments\n"
    #         "10. Extract each line item only if it has a non-zero amount and a valid SAC code\n"
    #         "11. Translate all service descriptions to English (e.g., 'कमरा किराया' → 'Room Tariff')\n\n"

    #         "CRITICAL TAX EXTRACTION — DO NOT CALCULATE:\n"
    #         "- NEVER calculate tax amounts by applying percentages to service amounts\n"
    #         "- ALWAYS read tax amounts directly from the 'Tax Summary' or invoice body\n"
    #         "- Look for patterns like 'Central GST @ 6.00%: 270.00' or 'State GST @ 9.00%: 130.05'\n"
    #         "- Use the EXACT amounts shown after the colon, not calculated values\n"
    #         "- Match each service item to its correct tax rate and assign corresponding SGST/CGST amounts\n\n"

    #         "TAX MATCHING PROCESS FOR HOTELS:\n"
    #         "1. Identify each service item (Room Tariff, Dining, etc.) and its SAC code\n"
    #         "2. Find the tax lines near it (same date or group) with the matching percentage\n"
    #         "3. Assign exact SGST and CGST amounts to that service line\n"
    #         "4. DO NOT sum or combine taxes for multiple services\n"

    #         "EXAMPLE TAX MATCHING:\n"
    #         "If service table shows:\n"
    #         "- Room Tariff: 3285.00, SAC: 996311, Tax: CGST @ 6%, SGST @ 6% → use 197.10 + 197.10\n"
    #         "- Food 1: 812.38, SAC: 996332, CGST/SGST @ 2.5% → use 20.31 + 20.31\n"
    #         "- Food 2: 224.74, SAC: 996332, CGST/SGST @ 2.5% → use 5.63 + 5.63\n\n"

    #         "TRANSLATION EXAMPLES:\n"
    #         "- Hindi: 'होटल ताज' → 'Hotel Taj', 'कमरा किराया' → 'Room Tariff'\n"
    #         "- Bengali: 'হোটেল সোনার গাঁও' → 'Hotel Sonargaon', 'রুম ভাড়া' → 'Room Rent'\n"
    #         "- Tamil: 'ஹோட்டல் சென்னை' → 'Hotel Chennai', 'அறை கட்டணம்' → 'Room Charge'\n\n"

    #         "FORMATTING:\n"
    #         "- All dates in ISO format: YYYY-MM-DD\n"
    #         "- All amounts as exact decimals (no commas, preserve precision)\n"
    #         "- All text fields in English\n\n"

    #         "Return complete hotel invoice data using Tax Summary values only. Ensure all fields are filled precisely, and no tax or service item is missed or merged."
    #     )

    @staticmethod
    def get_hotel_prompt():
        """Detailed prompt specifically for hotel invoices with language support"""
        return (
            "This is a HOTEL INVOICE. Extract ALL information with EXACT precision.\n\n"
            
            f"{InvoicePrompts.get_language_instruction()}"
            
            "CRITICAL EXTRACTION RULES:\n"
            "1. Read ALL numbers with EXACT decimal precision as shown (e.g., 270.05 NOT 270.00)\n"
            "2. Look at the main service items table AND the tax summary section\n"
            "3. Extract SGST/CGST amounts from the 'Tax Summary' section - these are official amounts\n"
            "4. For hotel_service_breakage: Include ONLY service items like Room Tariff, In-Room Dining, etc.\n"
            "5. DO NOT include separate tax line items in service breakage\n"
            "6. Match service items with their corresponding SAC codes and tax rates\n"
            "7. Extract the currency if shown — use standard abbreviation:\n"
            "   - ₹ = INR\n"
            "   - $ = USD\n"
            "   - € = EUR\n"
            "   - £ = GBP\n"
            "   - If currency is not mentioned, default to 'INR'\n"
            "8. Add a `type` field to each item in `hotel_service_breakage` to indicate the category of service:\n"
            "   - 'accommodation' for room tariff\n"
            "   - 'food' for in-room dining, restaurant services\n"
            "   - 'laundry', 'spa', 'transport' or other categories if mentioned\n"
            "9. Translate all service descriptions to English (e.g., 'कमरा किराया' → 'Room Tariff')\n\n"
            "CRITICAL TAX EXTRACTION - DO NOT CALCULATE, ONLY READ:\n"
            "- NEVER calculate tax amounts by applying percentages to service amounts\n"
            "- ALWAYS read tax amounts directly from the 'Tax Summary' section\n"
            "- Look for patterns like 'Central GST @ 6.00%: 270.00' or 'State GST @ 9.00%: 130.05'\n"
            "- Use the EXACT amounts shown after the colon, not calculated values\n"
            "- Match each service to its tax rate (6% or 9%) and use corresponding amounts from summary\n\n"
            "TAX MATCHING PROCESS FOR HOTELS:\n"
            "1. Identify each service item (Room Tariff, In-Room Dining, etc.) and its tax rate\n"
            "2. Find the matching tax rate lines in Tax Summary section\n"
            "3. Extract exact amounts (e.g., 'State GST @ 9.00%: 130.05' → use 130.05)\n"
            "4. Assign these exact amounts to corresponding service items\n"
            "5. DO NOT multiply service amounts by tax percentages\n\n"
            
            "EXAMPLE TAX MATCHING:\n"
            "If Tax Summary shows:\n"
            "- Central GST @ 6.00%: 270.00\n"
            "- Central GST @ 9.00%: 130.05\n"
            "- State GST @ 6.00%: 270.05\n"
            "- State GST @ 9.00%: 130.05\n"
            "Then assign 270.00/270.05 to 6% services and 130.05/130.05 to 9% services\n\n"
            
            "TRANSLATION EXAMPLES:\n"
            "- Hindi: 'होटल ताज' → 'Hotel Taj', 'कमरा किराया' → 'Room Tariff'\n"
            "- Bengali: 'হোটেল সোনার গাঁও' → 'Hotel Sonargaon', 'রুম ভাড়া' → 'Room Rent'\n"
            "- Tamil: 'ஹோட்டல் சென்னை' → 'Hotel Chennai', 'அறை கட்டணம்' → 'Room Charge'\n\n"
            
            "FORMATTING:\n"
            "- All dates in ISO format: YYYY-MM-DD\n"
            "- All amounts as exact decimals (no commas, preserve precision)\n"
            "- All text fields in English\n\n"
            
            "Return complete hotel invoice data using Tax Summary amounts only with all information translated to English."
        )
    
    @staticmethod
    def get_travel_prompt():
        """Detailed prompt specifically for travel invoices with language support"""
        return (
            "This is a TRAVEL INVOICE. Extract ALL information with EXACT precision.\n\n"
            
            f"{InvoicePrompts.get_language_instruction()}"
            
            "CRITICAL EXTRACTION RULES:\n"
            "1. Read ALL numbers with EXACT decimal precision as shown\n"
            "2. Look for travel-specific details like routes, dates, passenger info\n"
            "3. Extract tax amounts from tax summary or breakdown sections\n"
            "4. Include travel service details (flights, trains, cabs, etc.)\n"
            "5. Extract the currency if shown — use standard abbreviation:\n"
            "   - ₹ = INR\n"
            "   - Rp = IDR (Indonesian Rupiah)\n"
            "   - $ = USD\n"
            "   - € = EUR\n"
            "   - £ = GBP\n"
            "   - If currency is not mentioned, default to 'INR'\n"
            "6. Translate all travel-related descriptions to English\n\n"
            
            "TRAVEL-SPECIFIC FIELDS TO EXTRACT:\n"
            "- merchant_name, invoice_no, total_amount, invoice_date\n"
            "- sgst_amount, cgst_amount, igst_amount (if applicable)\n"
            "- company_name, gst_no, passenger_name\n"
            "- travel_from, travel_to, travel_date\n"
            "- travel_type (flight/train/cab/bus)\n"
            "- ticket_number, seat_number, class_type\n"
            "- travel_service_breakage with service details\n\n"
            
            "TRANSLATION EXAMPLES:\n"
            "- Hindi: 'दिल्ली से मुंबई' → 'Delhi to Mumbai', 'हवाई जहाज़' → 'Flight'\n"
            "- Bengali: 'কলকাতা থেকে দিল্লি' → 'Kolkata to Delhi', 'ট্রেন' → 'Train'\n"
            "- Regional stations: Translate to commonly used English names\n\n"
            
            "FORMATTING:\n"
            "- All dates in ISO format: YYYY-MM-DD\n"
            "- All amounts as exact decimals\n"
            "- All text fields in English\n\n"
            
            "Return complete travel invoice data with all information translated to English."
        )
    
    @staticmethod
    def get_food_prompt():
        """Detailed prompt specifically for food invoices with language support"""
        return (
            "This is a FOOD INVOICE. Extract ALL information with EXACT precision.\n\n"
            
            f"{InvoicePrompts.get_language_instruction()}"
            
            "CRITICAL EXTRACTION RULES:\n"
            "1. Read ALL numbers with EXACT decimal precision as shown\n"
            "2. Look for food items, quantities, and prices\n"
            "3. Extract tax amounts from tax breakdown sections\n"
            "4. Include food service details and item breakdowns\n"
            "5. Extract the currency if shown — use standard abbreviation:\n"
            "   - ₹ = INR\n"
            "   - $ = USD\n"
            "   - € = EUR\n"
            "   - £ = GBP\n"
            "   - If currency is not mentioned, default to 'INR'\n"
            "6. Translate all food items and restaurant details to English\n\n"
            
            "FOOD-SPECIFIC FIELDS TO EXTRACT:\n"
            "- merchant_name: Look for restaurant name at top of receipt (translate if needed)\n"
            "- invoice_no: Look for receipt number, order number, or bill number\n"
            "- total_amount: Final total amount (应付金额, 合计, Total, etc.)\n"
            "- invoice_date: Date from receipt header or timestamp\n"
            "- sgst_amount, cgst_amount, service_charge: Extract if present\n"
            "- company_name, gst_no, customer_name: Extract if available\n"
            "- restaurant_name: Same as merchant_name unless different\n"
            "- restaurant_address: Full address if shown\n"
            "- table_number: Table number if mentioned\n"
            "- order_type: dine-in/takeaway/delivery (infer from context)\n"
            "- food_items_breakage: ALL items with quantities, unit prices, and total prices\n"
            "- Include alcohol/beverage items separately if present\n"
            "- Look for items in columns: item_name, quantity, unit_price, total_price\n\n"
            
            "TRANSLATION EXAMPLES:\n"
            "- Hindi: 'बटर चिकन' → 'Butter Chicken', 'नान' → 'Naan'\n"
            "- Bengali: 'মাছের ঝোল' → 'Fish Curry', 'ভাত' → 'Rice'\n"
            "- Chinese: '白酒' → 'White Wine/Liquor', '啤酒' → 'Beer', '红烧肉' → 'Braised Pork'\n"
            "- Keep authentic dish names but add English descriptions where helpful\n"
            "- For alcohol/liquor items, clearly identify the type (wine, beer, spirits, etc.)\n\n"
            
            "FORMATTING:\n"
            "- All dates in ISO format: YYYY-MM-DD\n"
            "- All amounts as exact decimals\n"
            "- All text fields in English\n\n"
            
            "Return complete food invoice data with all information translated to English."
        )
    
    @staticmethod
    def get_other_prompt():
        """Generic prompt for other invoice types with language support"""
        return (
            "This is a GENERAL INVOICE. Extract ALL information with EXACT precision.\n\n"
            
            f"{InvoicePrompts.get_language_instruction()}"
            
            "CRITICAL EXTRACTION RULES:\n"
            "1. Read ALL numbers with EXACT decimal precision as shown\n"
            "2. Extract all visible tax information\n"
            "3. Include service/product details as available\n"
            "4. Translate all service/product descriptions to English\n\n"
            
            "GENERAL FIELDS TO EXTRACT:\n"
            "- merchant_name, invoice_no, total_amount, invoice_date\n"
            "- sgst_amount, cgst_amount, igst_amount (if applicable)\n"
            "- company_name, gst_no, customer_name\n"
            "- service_description, items_breakage\n\n"
            
            "FORMATTING:\n"
            "- All dates in ISO format: YYYY-MM-DD\n"
            "- All amounts as exact decimals\n"
            "- All text fields in English\n\n"
            
            "Return complete invoice data with all information translated to English."
        )
