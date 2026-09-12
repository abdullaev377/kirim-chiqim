import re
from rest_framework.exceptions import ValidationError
from rest_framework import status


phone_regex = re.compile(r'^998(9[012345789]|6[125679]|7[01234567])[0-9]{7}$')
email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def check_email_or_phone(data):
    if data.startswith('+'):
        data = data[1:]
    if re.fullmatch(phone_regex, data):
        return 'phone'
    elif re.fullmatch(email_regex, data):
        return 'email'
    else:
        raise ValidationError(
           { 'msg': 'Siz xato email yoki telefon raqam kiritdingiz--',
           'status': status.HTTP_400_BAD_REQUEST}
        )
        
        
        


