## Details of the different datatype variable values used in the data_parsing app
from decouple import config
import openai 

openai.api_key = config('OPENAI_SECRET_KEY')


## Date conversion and extraction module variable repository

is_date_part_function_param_values = {
            'date_extra_portion_list':['rd','nd','st','th']
}

month_list = ['january','february','march','april',
             'may','june','july','august','september',
            'october','november','december']

month_list_abbv = ['jan','feb','mar','apr','may','jun','jul',
                  'aug','sept','sep','oct','nov','dec']

first_considered_year = 1950

month_str_full_int_dict = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
                            'july':7,'august':8,'september':9,'october':10,'november':11,
                            'december':12}

month_str_abbr_int_dict = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
                            'jul':7,'aug':8,'sept':9,'sep':9,'oct':10,'nov':11,'dec':12}



## Diffferent invoices functions repository

gst_validation_codes = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,
                                "A": 10, "B": 11, "C": 12, "D": 13, "E": 14,
                                "F": 15, "G": 16, "H": 17, "I": 18, "J": 19,
                                "K": 20, "L": 21, "M": 22, "N": 23, "O": 24,
                                "P": 25, "Q": 26, "R": 27, "S": 28, "T": 29,
                                "U": 30, "V": 31, "W": 32, "X": 33, "Y": 34,
                                "Z": 35,
                                }

gst_multiplier_list = [1,2,1,2,1,2,1,2,1,2,1,2,1,2]
gst_divisor = 36

hour = 'hour'
minute = 'minute'
second = 'second'
unit_image_process_time = 26
seconds_in_a_hr = 3600
seconds_in_a_min = 60


## Filtering functions repository

restricted_words_for_date = ['invoice','bill','date','dt']

number_mapping = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
        'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
        'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
        'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
        'eighty': 80, 'ninety': 90, 
    }
    
decimals_dict = {'hundred': 100, 'thousand': 1000, 'million': 1000000,'lakhs':100000, 'lakh':100000,
                 'crore':10000000,
                'billion': 1000000000, 
                'trillion': 1000000000000 }
unwanted_number_string_words = ['negative']
ignore_number_string_words = ['point']



## GPT extraction functions' repository

prompt_for_detecting_bill_type = "tell what type of bill it is? select one option: food bill or hotel bill or travel bill or supplier bill or others"

bill_types_list1 = ['food','travel','hotel']
bill_types_list2 = ['vendor','supplier']

prompt_for_extracting_hotel_service_breakege = '''
                    From the below context extract the date wise description and corresponding amount. 
                    Do not confuse with arrival and departure date and do not provide any 'answer' as key. 
                    Description should be services taken from hotels mentioned in that bill.
                    The key value should be the date in DD-MM-YYYY format, and under that key there should be a list of dictionary where 
                    description,amount,SAC_code should be keys and it's values is taken from bill.
                    Example: ['date':[{'description':'value','amount':'value','SAC_code':'value'}]]'''



## invoice_result_organizer repository

initial_data_fields_value = 'N/A'

data_filed_labels_dictionary = {
    'merchant_name':"Merchant Name",
    'invoice_no':"Invoice/Bill Number",
    'total_amount':"Total Payable Amount",
    'bill_date':"Billing Date",
    'mode_of_travel':"Flight or Train or Bus or Cab?",
    'travel_ticket_class':"Travel ticket class",
    'company_name':"Entity/Company Name",
    'gst_no':"GST Number of Entity/Company",
    'sgst_amount':'SGST Amount',
    'cgst_amount':'CGST Amount',
    'guest_name':"Guest Name",
    'checkin_date':"Hotel check-in date",
    'checkout_date':"Hotel check-out date",
    'total_days_stayed':"Number of days stayed",
    'hotel_state':"Hotel State",
    'hotel_city':"Hotel City",
    'hotel_pin':"Hotel Pincode",
    'from_location':'From Location',
    'to_location':'To Location',
    'departure_date':'Departure Date',
    'departure_time':'Departure Time',
    'arrival_date':'Arrival Date',
    'arrival_time':'Arrival Time',
    'no_of_km':'Number of Kilo Meters',
    'intra_or_inter_city_travel':'Is it a Intra-city or Inter-city Travel?',
    'currency':'Currency'
}

currency_value = 'INR'

not_found_field_msg = "Not Found"

wrongly_formatted_field_value = 0

extracted_dictionary_data_label = "image_data"

## Data parsing view function repository

request_parameter_text = 'bill_text'
request_parameter_bill_type = 'bill_type'

fields_for_food_n_travel_invoices = [data_filed_labels_dictionary['merchant_name'], 
                                     data_filed_labels_dictionary['invoice_no'],
                                     data_filed_labels_dictionary['bill_date'],
                                     data_filed_labels_dictionary['total_amount'],
                                     data_filed_labels_dictionary['sgst_amount'],
                                     data_filed_labels_dictionary['cgst_amount']]

fields_for_travel_invoices =        [data_filed_labels_dictionary['merchant_name'], 
                                     data_filed_labels_dictionary['invoice_no'],
                                     data_filed_labels_dictionary['bill_date'],
                                     data_filed_labels_dictionary['total_amount'],
                                     data_filed_labels_dictionary['mode_of_travel'],
                                     data_filed_labels_dictionary['travel_ticket_class'],
                                     data_filed_labels_dictionary['from_location'],
                                     data_filed_labels_dictionary['to_location'],
                                     data_filed_labels_dictionary['departure_date'],
                                     data_filed_labels_dictionary['departure_time'],
                                     data_filed_labels_dictionary['arrival_date'],
                                     data_filed_labels_dictionary['arrival_time'],
                                     data_filed_labels_dictionary['no_of_km'],
                                     data_filed_labels_dictionary['intra_or_inter_city_travel']
                                     ]

fields_for_hotel_invoices =    [data_filed_labels_dictionary['merchant_name'], 
                                data_filed_labels_dictionary['invoice_no'],
                                data_filed_labels_dictionary['bill_date'],
                                data_filed_labels_dictionary['total_amount'],
                                data_filed_labels_dictionary['guest_name'],
                                data_filed_labels_dictionary['company_name'],
                                data_filed_labels_dictionary['gst_no'],
                                data_filed_labels_dictionary['checkin_date'],
                                data_filed_labels_dictionary['checkout_date'],
                                data_filed_labels_dictionary['total_days_stayed'],
                                data_filed_labels_dictionary['hotel_state'],
                                data_filed_labels_dictionary['hotel_city'],
                                data_filed_labels_dictionary['hotel_pin']]
      
initial_empty_service_breakage = []


class common_output_dictionary:
    def get_empty_common_dictionary(self):

        common_output_dictionary = {'filename':'N/A',
                                'bill_type':'N/A',
                                'merchant_name': 'N/A',
                                'guest_name':'N/A',
                                'invoice_no': 'N/A',
                                'gst_no': 'N/A',
                                'sgst_amount': 'N/A',
                                'cgst_amount':'N/A',
                                'company_name': 'N/A',
                                'total_amount': 'N/A',
                                'date': 'N/A',
                                'checkin_date':'N/A',
                                'checkout_date':'N/A',
                                'total_days_stayed':'N/A',
                                'total_amount': 'N/A',
                                'mode_of_travel':'N/A',
                                'travel_ticket_class':'N/A',
                                'from_location':'N/A',
                                'to_location':'N/A',
                                'departure_date':'N/A',
                                'departure_time':'N/A',
                                'arrival_date':'N/A',
                                'arrival_time':'N/A',
                                'no_of_km':'N/A',
                                'intra_or_inter_city_travel':'N/A',
                                'hotel_state':'N/A',
                                'hotel_city':'N/A',
                                'hotel_pin':'N/A',
                                'currency': 'N/A',
                                'hotel_service_breakage':initial_empty_service_breakage}
        
        
        return common_output_dictionary

filename = 'Sample_image.jpg' 

not_found_msg = "Not Found"
food_bill_type = 'food'
travel_bill_type = 'conveyance'
hotel_bill_type = 'hotel'
supplier_bill_type = 'supplier'
others_bill_type = 'others'

error_json_respone = 'Not an image file'

result_filename = "Results.csv"


## sac_code_wise_segregration_repo repository

SAC_code_description = {
                '996311': 'accommodation',
                '996322': 'accommodation',
                '996329': 'accommodation',
                '996331': 'food',
                '996332': 'food',
                '996333': 'food',
                '996334': 'food',
                '996335': 'food',
                '996336': 'food',
                '996337': 'food',
                '996339': 'food',
                '996733': 'laundry',
                '996712': 'transportation',
                '996714': 'transportation',
                '998722': 'housekeeping',
                '999529': 'spa',
                '999511': 'gym',
                '998416': 'internet',
                '996721': 'business center',
                '996722': 'meeting and conference room rental',
                '998723': 'event planning and management',
                '996713': 'airport transfer'
            }

sac_code_list=sac_code_list = list(SAC_code_description.keys())

food_service_type_words= ['food','dinner','lunch','dining','meal','resturant','breakfast',
                        'beverage','cafeteria','refreshment','snack']

accommodation_service_type_words=['accommodation','accommodation','tariff','lodging',
                                 'room charge','room rate','nightly','stay','guestroom','overnight',
                                 'housing','suite','boarding','residential','lodgement']



## views function repositories

response_message_field = 'message'

response_message_parameters_not_found = "One or more parameter values are not correctly supplied! Please retry with proper values."

response_message_bill_type_not_matched = "Please upload a valid bill type."

response_message_success = "success"

response_extracted_data = "extracted_data" 

response_bad_request_method = "Bad request method type."


## New conveyance configurations

image_converted_status_bad_request = "Failed to reconstruct image at server side."
image_format_status_bad_request = "The API response does not contain a valid image."
image_converted_status_success = "success"
bad_request_method_message = "Bad HTTP request type. Use POST request type."

response_message_label = "message"
response_text_label = "text"

# Define a custom dictionary to map month names to their abbreviations
month_abbreviations = {
    'JANUARY': 'JAN',
    'FEBRUARY': 'FEB',
    'MARCH': 'MAR',
    'APRIL': 'APR',
    'MAY': 'MAY',
    'JUNE': 'JUN',
    'JULY': 'JUL',
    'AUGUST': 'AUG',
    'SEPTEMBER': 'SEP',
    'OCTOBER': 'OCT',
    'NOVEMBER': 'NOV',
    'DECEMBER': 'DEC'
}


fields_to_extract_for_conveyance = ["From Location","To Location", "Departure Date", "Departure Time", 
                     "Arrival Date", "Arrival Time","Number of Kilo Meters", 
                     "Is it a Intra-city or Inter-city Travel?"]

