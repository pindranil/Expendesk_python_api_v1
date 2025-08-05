import openai
import ast
import random
import time
import json
from openai import RateLimitError

from invoice_extraction.configuration import *

prompt_for_detecting_bill_type = prompt_for_detecting_bill_type
bill_types_list1 = bill_types_list1
bill_types_list2 = bill_types_list2
prompt_for_extracting_hotel_service_breakege = prompt_for_extracting_hotel_service_breakege
not_found_msg = not_found_msg
supplier_bill_type = supplier_bill_type




## ___________________________      GPT prompts and extraction function     ___________________________##

# Define a retry decorator
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (RateLimitError,),
):
    """Retry a function with exponential backoff."""
    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)

            # Retry on specific errors
            except errors as e:
                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e
    return wrapper


# @retry_with_exponential_backoff
# def detect_bill_type(text):
#     # Define your prompt
#     prompt = text + "\n" + prompt_for_detecting_bill_type

#     # Generate the response using the ChatGPT model
#     response = openai.Completion.create(
#         engine='text-davinci-003',
#         prompt=prompt,
#         max_tokens=10,
#         n=1,
#         stop=None,
#         temperature=0.0,
#     )
#     # Extract the extracted fields and their values from the response

#     for invoice_type in bill_types_list1:
#         try:
#             if invoice_type in response.choices[0].text.strip().lower():
#                 return invoice_type
#         except:
#             return not_found_msg

#     for invoice_type in bill_types_list2:
#         try:
#             if invoice_type in response.choices[0].text.strip().lower():
#                 return supplier_bill_type
#         except:
#             return not_found_msg
        
#     return not_found_msg



@retry_with_exponential_backoff
## Prompt slightly changed 
def extract_fields(input_string, fields):
    # Define your prompt
    prompt = "Extract the following fields:\n" + input_string + "\n---\nFields: " + ", ".join(fields) + "\n If any field is not found return 'Not Found'---"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
        ],
        max_tokens=400,
        n=1,
        stop=None,
        temperature=0.0,
    )
    
    # Extract the extracted fields and their values from the response
    extracted_fields = {}
    
    try:
        response_text = response['choices'][0]['message']['content'].strip().split('\n')
    except:
        pass

    if 'merchant name' not in (response_text[0]).lower():
        response_text=response_text[1:]
    else:
        response_text=response_text

    # print(response_text)

    field_index = 0
    
    if len(response_text) == 1:
        response_text = [i for i in response_text[0].split(",") if i!=' ' and i!='']
        
    for line in response_text:  
        # for field in fields:
        try:
            if fields[field_index] in line:
                field_value = line.replace(fields[field_index]+":", "").strip()
            else:
                field_value = line

            extracted_fields[fields[field_index]] = field_value
        except:
            pass
   
        field_index+=1

    return extracted_fields




@retry_with_exponential_backoff
def extract_hotel_service_breakage(input_string):
    # Define your prompt
    # Define your prompt
    prompt =  prompt_for_extracting_hotel_service_breakege+input_string

    # Generate the response using the ChatGPT model
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
        ],
        max_tokens=1200,
        n=1,
        stop=None,
        temperature=0.0,
    )
    
    #print(response)
    # Extract the extracted fields and their values from the response
    hotel_breakage_list = []
    dict_output = {}
    
    answer_string = response['choices'][0]['message']['content'].strip().split('\n')

    #print(answer_string)
    
    try:
        answer_string = str(answer_string)
        answer_string = answer_string.split("Answer:", 1)[-1].strip()
    except:
        pass
    
    list_of_str_output = []
    
    try:  
        list_of_str_output = ast.literal_eval(answer_string)
    except:
        pass
    
    jsonable_string = ''

    for string in list_of_str_output:
        jsonable_string+=string
    
    if jsonable_string != '':
        
        dict_output = json.loads(jsonable_string)

        for a_key in dict_output.keys():
            for breakage_result in dict_output[a_key]:
                breakage_result['date'] = a_key
                hotel_breakage_list.append(breakage_result)
                
    return hotel_breakage_list
