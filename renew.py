# encoding: utf-8
"""
Crontab script to renew public IP(obtained by PPPoE or ADSL) to name.com as an A record.
"""
import requests




def get_public_ip():
    resp = requests.get("https://api.ipify.org?format=json")
    return resp.json()['ip']

def list_records(username, password, domain_name):
    """
    by default, 1000 per page, according to api docs
    """
    path = "https://api.name.com/v4/domains/%s/records" % domain_name
    resp = requests.get(path, auth=(username, password))
    return resp.json()['records']

def search_record(username, password, domain_name, host_name):
    records = list_records(username, password, domain_name)
    try:
        return next(x for x in records if 'host' in x and x['host'] == host_name)
    except StopIteration:
        return None


def update_record(username, password, domain_name, 
        record_id, host_name, type_value, answer_value, ttl=300):
    path = "https://api.name.com/v4/domains/%s/records/%s" % (domain_name, record_id)
    resp = requests.put(path, auth=(username, password), json={
        "id": record_id,
        "host": host_name,
        "type": "A",
        "answer": answer_value,
        "ttl": ttl
        })
    resp.raise_for_status()
    return resp.json()


def create_record(username, password, domain_name,
        host_name, type_value, answer_value, ttl=300):
    path = "https://api.name.com/v4/domains/%s/records" % (domain_name)
    resp = requests.post(path, auth=(username, password), json={
        "host": host_name,
        "type": "A",
        "answer": answer_value,
        "ttl": ttl
        })
    resp.raise_for_status()
    return resp.json()


from config_prod import *

if __name__ == '__main__':
    public_ip = get_public_ip()
    print('public ip:', public_ip)
    record = search_record(AUTH_USER, AUTH_PASS, DOMAIN_NAME, HOST_NAME)
    if record == None:
        data = create_record(AUTH_USER, AUTH_PASS, DOMAIN_NAME, 
            HOST_NAME, "A", public_ip, ttl=300)
        print('fqdn created:', data['fqdn'])
    elif record['answer'] == public_ip:
        print('no need to update')
    else:
        data = update_record(AUTH_USER, AUTH_PASS, DOMAIN_NAME, 
            record['id'], HOST_NAME, "A", public_ip, ttl=300)
        print('fqdn updated:', data['fqdn'])




