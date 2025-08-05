from django.conf import settings

from invoice_extraction.configuration import *
from invoice_extraction.gpt_extraction_functions import *
from invoice_extraction.conveyance_newfields_parsing_functions import *

from invoice_extraction.line_item_segregation_module import line_item_categorise

line_item_categorise_obj=line_item_categorise
common_dict_obj = common_output_dictionary()


## ___________________________  Food bill results storing  ___________________________##

def get_food_bills_fields(fields,text,filename):
        print("*****ABCD",fields)
        merchant_name = initial_data_fields_value
        invoice_no =    initial_data_fields_value
        total_amount =  initial_data_fields_value
        date =          initial_data_fields_value
        currency =      initial_data_fields_value
        state_gst=      initial_data_fields_value
        central_gst=    initial_data_fields_value

        image_data = common_dict_obj.get_empty_common_dictionary()

        try:
            merchant_name = fields[data_filed_labels_dictionary['merchant_name']]
        except:
            merchant_name= not_found_field_msg
        
        try:
            invoice_no = fields[data_filed_labels_dictionary['invoice_no']]
        except:
            invoice_no=not_found_field_msg

        try:
            total_amount = fields[data_filed_labels_dictionary['total_amount']]
        except:
            total_amount=not_found_field_msg

        try:
            date=fields[data_filed_labels_dictionary['bill_date']]
        except:
            date=not_found_field_msg  

        try:
            state_gst=fields[data_filed_labels_dictionary['sgst_amount']]
        except:
            state_gst=not_found_field_msg  

        try:
            central_gst=fields[data_filed_labels_dictionary['cgst_amount']]
        except:
            central_gst=not_found_field_msg  

        try:
            currency = currency_value
        except:
            currency=not_found_field_msg

        image_data['filename'] = filename
        image_data['bill_type'] = food_bill_type
        image_data['merchant_name'] =  merchant_name
        image_data['invoice_no'] =  invoice_no
        image_data['total_amount'] = total_amount
        image_data['date'] =  date
        image_data['currency'] =  currency
        image_data['sgst_amount'] = state_gst
        image_data['cgst_amount'] = central_gst
        
        return {extracted_dictionary_data_label: image_data}



## ___________________________  Travel bill results storing  ___________________________##

def get_travel_bills_fields(fields,text,filename):

        # print("*****")  
        # print(fields)
    
        merchant_name = initial_data_fields_value
        invoice_no =    initial_data_fields_value
        total_amount =  initial_data_fields_value
        date =          initial_data_fields_value
        currency =      initial_data_fields_value
        travel_ticket_class = initial_data_fields_value
        from_location = initial_data_fields_value
        to_location = initial_data_fields_value
        departure_date = initial_data_fields_value
        departure_time  = initial_data_fields_value
        arrival_date = initial_data_fields_value
        arrival_time = initial_data_fields_value
        no_of_hours = initial_data_fields_value
        no_of_km = initial_data_fields_value
        intra_or_inter_city_travel = initial_data_fields_value
        currency =  initial_data_fields_value

        image_data = common_dict_obj.get_empty_common_dictionary()

        try:
            merchant_name = fields[data_filed_labels_dictionary['merchant_name']]
        except:
            merchant_name= not_found_field_msg
        
        try:
            invoice_no = fields[data_filed_labels_dictionary['invoice_no']]
        except:
            invoice_no=not_found_field_msg

        try:
            total_amount = fields[data_filed_labels_dictionary['total_amount']]
        except:
            total_amount=not_found_field_msg
            
        try:
            date=fields[data_filed_labels_dictionary['bill_date']]
        except:
            date=not_found_field_msg   

        try:
            mode_of_travel = fields[data_filed_labels_dictionary['mode_of_travel']]
        except:
            mode_of_travel = not_found_field_msg
        
        try:
            travel_ticket_class = fields[data_filed_labels_dictionary['travel_ticket_class']]
        except:
            travel_ticket_class = not_found_field_msg

        # try:
        from_location = fields[data_filed_labels_dictionary['from_location']]
        # except:
        #from_location = not_found_field_msg

        # try:
        to_location = fields[data_filed_labels_dictionary['to_location']]
        # except:
        #to_location = not_found_field_msg

        departure_date = fields[data_filed_labels_dictionary['departure_date']]

        departure_time = fields[data_filed_labels_dictionary['departure_time']]
        
        arrival_date = fields[data_filed_labels_dictionary['arrival_date']]

        arrival_time = fields[data_filed_labels_dictionary['arrival_time']]

        no_of_hours = get_calculated_journey_time(fields)

        no_of_km = fields[data_filed_labels_dictionary['no_of_km']]

        intra_or_inter_city_travel = fields[data_filed_labels_dictionary['intra_or_inter_city_travel']]

        try:
            currency = currency_value
        except:
            currency=not_found_field_msg

        image_data['filename'] = filename
        image_data['bill_type'] = travel_bill_type
        image_data['merchant_name'] =  merchant_name
        image_data['invoice_no'] =  invoice_no
        image_data['total_amount'] = total_amount
        image_data['date'] =  date
        image_data['currency'] =  currency
        image_data['mode_of_travel'] = mode_of_travel
        image_data['travel_ticket_class'] = travel_ticket_class
        image_data['from_location'] = from_location
        image_data['to_location'] = to_location
        image_data['departure_date'] = departure_date
        image_data['departure_time'] = departure_time
        image_data['arrival_date'] = arrival_date
        image_data['arrival_time'] = arrival_time
        image_data['no_of_hours'] = no_of_hours
        image_data['no_of_km'] = no_of_km
        image_data['intra_or_inter_city_travel'] = intra_or_inter_city_travel

        return {extracted_dictionary_data_label: image_data}



## ___________________________  Hotel bill results storing  ___________________________##

def get_hotel_bills_fields(fields,text,filename):
        
        merchant_name = initial_data_fields_value
        invoice_no =    initial_data_fields_value
        company_name =  initial_data_fields_value
        gst_no =        initial_data_fields_value
        total_amount =  initial_data_fields_value
        date =          initial_data_fields_value
        guest_name =    initial_data_fields_value
        company_name=   initial_data_fields_value
        checkin_date =  initial_data_fields_value
        checkout_date = initial_data_fields_value
        total_days_stayed = initial_data_fields_value
        currency = initial_data_fields_value
        hotel_state = initial_data_fields_value
        hotel_city = initial_data_fields_value
        hotel_pin = initial_data_fields_value

        image_data = common_dict_obj.get_empty_common_dictionary()
        
        # print("*** Hotel Fields before org. ")
        # print(fields)
        # print(" ")
        # print("***")
        
        try:
            merchant_name = fields[data_filed_labels_dictionary['merchant_name']]
        except:
            merchant_name= not_found_field_msg

        try:
            guest_name = fields[data_filed_labels_dictionary['guest_name']]
        except:
            guest_name=not_found_field_msg

        try:
            company_name = fields[data_filed_labels_dictionary['company_name']]
        except:
            company_name = not_found_field_msg

        try:
            invoice_no = fields[data_filed_labels_dictionary['invoice_no']]
        except:
            invoice_no=not_found_field_msg

        try:
            total_amount = fields[data_filed_labels_dictionary['total_amount']]
        except:
            total_amount=not_found_field_msg

        try:
            date=fields[data_filed_labels_dictionary['bill_date']]
        except:
           date=not_found_field_msg

        try:
            gst_no = fields[data_filed_labels_dictionary['gst_no']]
        except:
            gst_no=wrongly_formatted_field_value

        try:
            checkin_date = fields[data_filed_labels_dictionary['checkin_date']]
        except:
            checkin_date=not_found_field_msg
        
        try:
            checkout_date = fields[data_filed_labels_dictionary['checkout_date']]
        except:
            checkout_date=not_found_field_msg

        try:
            total_days_stayed=fields[data_filed_labels_dictionary['total_days_stayed']]
        except:
            total_days_stayed=not_found_field_msg
          
        try:
            currency = currency_value
        except:
            currency=not_found_field_msg

        try:
            hotel_state = fields[data_filed_labels_dictionary['hotel_state']]
        except:
            hotel_state = not_found_field_msg

        try:
            hotel_city = fields[data_filed_labels_dictionary['hotel_city']]
        except:
            hotel_city = not_found_field_msg

        try:
            hotel_pin = fields[data_filed_labels_dictionary['hotel_pin']]
        except:
            hotel_pin = not_found_field_msg

        hotel_services_breakage = extract_hotel_service_breakage(text)
        hotel_services_breakage=line_item_categorise_obj.line_item_categorisation(hotel_services_breakage)

        image_data['filename'] = filename
        image_data['bill_type'] = hotel_bill_type
        image_data['merchant_name'] =  merchant_name
        image_data['invoice_no'] =  invoice_no
        image_data['total_amount'] = total_amount
        image_data['date'] =  date
        image_data['company_name'] = company_name
        image_data['guest_name'] = guest_name
        image_data['gst_no'] = gst_no
        image_data['checkin_date'] = checkin_date
        image_data['checkout_date'] = checkout_date
        image_data['total_days_stayed'] = total_days_stayed
        image_data['hotel_state'] = hotel_state
        image_data['hotel_city'] = hotel_city
        image_data['hotel_pin'] = hotel_pin
        image_data['hotel_service_breakage']=hotel_services_breakage
        image_data['currency'] =   currency


        return {extracted_dictionary_data_label: image_data}



## ___________________________  Vendor/Supplier bill results storing  ___________________________##

# def get_vendor_bill_fields(fields,text,filename):

#     file_name = filename
#     bill_type = 'vendor/supplier'
#     merchant_name = 'N/A'
#     invoice_no = 'N/A'
#     company_name = 'N/A'
#     gst_no = 'N/A'
#     total_amount = 'N/A'
#     date = 'N/A'
#     guest_name = 'N/A'
#     checkin_date = 'N/A'
#     checkout_date = 'N/A'
#     total_days_stayed = 'N/A'
#     currency = 'N/A'
#     hotel_services_breakage='N/A'
#     mode_of_travel = 'N/A'
#     travel_ticket_class = 'N/A'
#     liquor_status = 'N/A'
#     hotel_state = 'N/A'
#     hotel_city = 'N/A'
#     hotel_pin = 'N/A'

#     temporary_list = []
#     image_data = []

#     try:
#         merchant_name = filter_merchant_name(fields['Merchant Name'])
#     except:
#         merchant_name='Not Found'
    
#     try:
#         invoice_no = filter_invoice_no(fields['Invoice/Bill Number'])
#     except:
#         invoice_no='Not Found'
    
#     gst_format=1

#     try:
#         gst_no = filter_invoice_no(fields['GST Number'])
#         #gst_format=(gst_validation_algo(gst_no))['format']
#     except:
#         #print("Here in except!!!!!!!!!")
#         gst_no='Not Found'
#         gst_format=0

#     try:
#         total_amount = filter_total_amount(fields['Total Payable Amount'])
#         total_amount=total_amount.replace(",",'')
#         total_amount=str(total_amount)
#         total_amount = total_amount_check(total_amount)['total_amount']
#         total_amount_format = total_amount_check(total_amount)['format'] 
#     except:
#         total_amount='Not Found'
#         total_amount_format=0

#     try:
#         date=date_conv_obj.get_dd_mm_yyyy_string(filter_invoice_date(fields['Billing Date']))['date']
#         format=date_conv_obj.get_dd_mm_yyyy_string(filter_invoice_date(fields['Billing Date']))['format']
#         # date = date_conv_obj.get_dd_mm_yyyy_string(filter_invoice_date(extracted_fields['Billing Date']))
#         if len(date)<6:
#             try:
#                 date=date_conv_obj.get_dd_mm_yyyy_string((date_ext_obj.date_extractor(text)['invoice_date']))['date']
#                 format=date_conv_obj.get_dd_mm_yyyy_string((date_ext_obj.date_extractor(text)['invoice_date']))['format']
#             except:
#                 date="Not Found"  
#                 format=0                  
#     except:
#         try:
#             date=date_conv_obj.get_dd_mm_yyyy_string((date_ext_obj.date_extractor(text)['invoice_date']))['date']
#             format=date_conv_obj.get_dd_mm_yyyy_string((date_ext_obj.date_extractor(text)['invoice_date']))['format']
#         except:
#             date="Not Found"
#             format=0  
#     try:
#         currency = "INR"
#     except:
#         currency='Not Found'

#     hotel_services_breakage=[]

#     temporary_list = [file_name, bill_type, merchant_name, invoice_no, 
#                     total_amount,date, mode_of_travel,travel_ticket_class, company_name, 
#                     gst_no, guest_name,hotel_state,hotel_city,hotel_pin,checkin_date, 
#                     checkout_date, total_days_stayed,
#                     liquor_status, hotel_services_breakage,currency,][:]

#     # print(temporary_list)

#     image_data.append({
#         'filename': filename,
#         'link': f"{settings.MEDIA_URL}{filename}",
#         'merchant_name': merchant_name,
#         'invoice_no': invoice_no,
#         'gst_no': gst_no,
#         'gst_format':gst_format,
#         'total_amount': total_amount,
#         'total_amount_format': total_amount_format,
#         'format': format,
#         'date': date,
#         'currency': currency,
#         'hotel_service_breakage':hotel_services_breakage,
#         'bill_type':'vendor/supplier'
#     })
    
#     return {'image_data': image_data,'temporary_list': temporary_list}




## _________________    Get image data for food, travel, hotel and vendor/supplier bills    __________________#

def get_image_data(bill_type, fields,text,filename):

    temporary_functions_dict = {
        'food':get_food_bills_fields,
        'conveyance':get_travel_bills_fields,
        'hotel': get_hotel_bills_fields,
        # 'vendor/supplier':get_vendor_bill_fields,
    }

    # try
    return temporary_functions_dict[bill_type](fields,text,filename)