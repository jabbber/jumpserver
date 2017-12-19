import requests
import json
from django.conf import settings

def auth(username,password):
    try:
        result = requests.post(settings.CONFIG.AUTH_3RD_URL,data=dict(name=username,password=password),timeout=3)
    except Exception as error:
        return False,'{}: {}'.format(type(error),error)
    else:
        status_code = result.status_code
        message = result.text
    flash_type = 'error'
    is_authenticated = False
    if result.status_code == 200:
        try:
            r = json.loads(result.text)
        except json.decoder.JSONDecodeError:
            pass
        else:
            message = r.get('message')
            status_code = r.get('status')
            if r.get('status') == 200:
                is_authenticated = True
                flash_type = 'alert alert-success'
    return is_authenticated,result.text

if __name__ == '__main__':
    import sys
    print(auth(sys.argv[1],sys.argv[2]))
