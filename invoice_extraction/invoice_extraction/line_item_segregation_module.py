from invoice_extraction.sac_code_segregation import repo_for_line_item_categorisation
from invoice_extraction.configuration import *


repo_for_line_item_categorisation_obj=repo_for_line_item_categorisation

SAC_code_description=repo_for_line_item_categorisation_obj.sac_code_description_dict()

sac_code_list=repo_for_line_item_categorisation_obj.sac_code_list_items()

food_service_type_words=repo_for_line_item_categorisation_obj.food_service_words()

accommodation_service_type_words=repo_for_line_item_categorisation_obj.accommodation_service_words()


### supporting functions ########
def food_service_type(description):
    service_type=''
    for word in food_service_type_words:
        if word in description.lower():
            service_type=food_bill_type 
            return service_type
        else:
            continue
    if service_type==food_bill_type:
        return (service_type)
    else:
        return('unknown')
    

def accommodation_service_type(description):
    service_type=''
    for word in accommodation_service_type_words:
        if word in description.lower():
            service_type='accommodation'
            
        else:
            continue
    if service_type=='accommodation':
        return (service_type)
    else:
        return('unknown')


#### main function ###

def line_item_categorisation(line_item_list):

    ## Added the below portion on 21st Nov to lowercase the "SAC_code" key.
    ##______________________________________________________________
    
    for eleJSON in line_item_list:
        try:
            eleJSON['sac_code'] = eleJSON["SAC_code"]
            del eleJSON['SAC_code']
        except:
            eleJSON['sac_code'] = ''
    ##______________________________________________________________

    derived_line_item_list=[]

    for ele in line_item_list:
        sac_code=ele['sac_code']

        if sac_code in sac_code_list:
            #print('yes')
            ele['service_type']=SAC_code_description[sac_code]
            derived_line_item_list.append(ele)

        else:
            #print('no')
            description=ele['description']
            if 'gst' in description.lower():
                ele['service_type']='gst'
                #print('gst_service')
                derived_line_item_list.append(ele)
            elif 'tax' in description.lower():
                ele['service_type']='gst'
                #print('gst_service')
                derived_line_item_list.append(ele)
            else:
                ele['service_type']='unknown'
                derived_line_item_list.append(ele)
                
    for ele in derived_line_item_list:
        if ele['service_type']=='unknown':
            description=ele['description']
            service_type=accommodation_service_type(description)
            #print(service_type)
            if service_type=='unknown':
                service_type=food_service_type(description)
            ele['service_type']=service_type
            #print(service_type)

        else:
            continue
    
    return (derived_line_item_list)
                
                

def associate_gst_with_segregated_services(segregated_hotel_line_items):
    
    last_service_encountered = None
    
    if not isinstance(segregated_hotel_line_items,list):
        return "error"
    
    copy_list = segregated_hotel_line_items
    
    for service_dictionary in segregated_hotel_line_items:

        # try:
        if service_dictionary['service_type'] =='gst' and last_service_encountered!=None:
            service_dictionary['service_type'] = last_service_encountered+" "+'gst'

        elif service_dictionary['service_type'] != 'gst':
            last_service_encountered=service_dictionary['service_type']
        # except:
        #     pass
            
    return segregated_hotel_line_items
                

class line_item_categorise:
    def line_item_categorisation(line_item_list):
        categorisation=line_item_categorisation(line_item_list)
        categorisation_2=associate_gst_with_segregated_services(categorisation)
        
        # print('*********************************')
        # print(categorisation_2) 
        # print('*********************************')
        return(categorisation_2)