import re
import requests
from lxml import etree

url = "" # appdrive url

MD = "" # md cookie
PHPSESSID = "" # phpsessid cookie

'''
NOTE: Auto-detection for non-login urls, and indicated via 'link_type' (direct/login) in output.
'''

# ===================================================================

def gen_payload(data, boundary=f'{"-"*6}_'):
    data_string = ''
    for item in data:
        data_string += f'{boundary}\r\n'
        data_string += f'Content-Disposition: form-data; name="{item}"\r\n\r\n{data[item]}\r\n'
    data_string += f'{boundary}--\r\n'
    return data_string

def parse_info(data):
    info = re.findall('>(.*?)<\/li>', data)
    info_parsed = {}
    for item in info:
        kv = [s.strip() for s in item.split(':', maxsplit = 1)]
        info_parsed[kv[0].lower()] = kv[1]
    return info_parsed

def appdrive_dl(url):
    client = requests.Session()
    
    client.cookies.update({
        'MD': MD,
        'PHPSESSID': PHPSESSID
    })

    res = client.get(url)
    key = re.findall('"key",\s+"(.*?)"', res.text)[0]

    ddl_btn = etree.HTML(res.content).xpath("//button[@id='drc']")

    info_parsed = parse_info(res.text)
    info_parsed['error'] = False
    info_parsed['link_type'] = 'login' # direct/login
    
    headers = {
        "Content-Type": f"multipart/form-data; boundary={'-'*4}_",
    }
    
    data = {
        'type': 1,
        'key': key
    }
    
    data['action'] = 'original'
    
    if len(ddl_btn):
        info_parsed['link_type'] = 'direct'
        data['action'] = 'direct'
        
    while data['type'] <= 3:
        try:
            response = client.post(url, data=gen_payload(data), headers=headers).json()
            break
        except:
            data['type'] += 1

    if 'url' in response:
        info_parsed['gdrive_link'] = response['url']
        
    elif 'error' in response and response['error']:
        info_parsed['error'] = True
        info_parsed['error_message'] = response['message']
        
    info_parsed['src_url'] = url
    
    return info_parsed

# ===================================================================

print(appdrive_dl(url))
