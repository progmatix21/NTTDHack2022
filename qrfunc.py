#!/usr/bin/env python3

import hashlib
import json
import qrcode
import cv2
import ast
from pyzbar import pyzbar

cardiodict = {'age':55, 'sbp':120, 'dbp':90, 'weight':75, 'height':150, 'chol':150}
              
def get_dict_hash(input_dict):
    '''
    Return hash of a dictionary
    Argument: dictionary
    Returns: hash
    '''
    result = hashlib.md5(json.dumps(input_dict, sort_keys =True).encode('utf-8'))
    hash_value = result.hexdigest()
    return(hash_value)
    
def dict_hash(input_dict):
    '''
    create a hash of a dictionary and insert into dictionary
    Arguments: dictionary
    Returns: same dictionary with hash inserted in key 'hash'
    '''
    hashed_dict = input_dict
    hash_value = get_dict_hash(input_dict)
    hashed_dict['hash'] = hash_value
    return(hashed_dict)   #Now with hash
    
def createqr(mydict, filename):
    '''
    create a qrcode with the input dict and write to file
    Arguments: input_dict
    Returns: a qrcode of the input_dict and saved to file with filename
    '''
    
    qr = qrcode.QRCode(
        version = None,
        error_correction = qrcode.constants.ERROR_CORRECT_M,
        box_size = 10,
        border = 4,
    )
    qr.add_data(str(mydict))
    qr.make(fit = True)
    
    img = qr.make_image(fill_color = (0,128,128), back_color = "White")
    img.save(filename)
    
def decodeqr(filename):
    '''
    decode the qrcode and obtain the original dict
    Arguments: filename
    Returns: original dict if valid else empty dict
    '''
    
    rimg = cv2.imread(filename)   #read the image
    rimg_grey = cv2.cvtColor(rimg, cv2.COLOR_BGR2GRAY) #convert to greyscale

    '''
    # Using OpenCV
    detector = cv2.QRCodeDetector()
    decoded_payload, bbox, _ = detector.detectAndDecode(rimg_grey)
    print(bbox)

    '''
    # Using PyZbar
    height, width = rimg_grey.shape[:2]
    decoded_obj = pyzbar.decode((rimg_grey.tobytes(), width, height))
    decoded_payload = decoded_obj[0][0].decode('utf-8') #dict as string



    print("Decoded payload: ", decoded_payload)
    rdict = ast.literal_eval(decoded_payload)   #get dict object
    #this is the 'signed' dict. We need to check if this is a valid signature
    
    #store the recvd hash 
    rhash = rdict['hash']
    #now remove the hash key and item from rdict
    del rdict['hash']

    #rdict['sbp'] = 121 #tampering
    #Now check if the returned hash agrees with the original dict
    if(get_dict_hash(rdict) == rhash):
        return(rdict)  #return dict object. Valid signature
    else:
        return(dict())  #return empty dict. Signature doesn't agree
        
if __name__ == "__main__":
    
    hdict = dict_hash(cardiodict)  #Sign dict with hash
    print(hdict)
    
    createqr(hdict, "cardio_test.png") #Create hashed dict file
    print(decodeqr("cardio_test.png"))
    

