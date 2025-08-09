import os
import requests
import time

virus_total_api_scan_url = "https://www.virustotal.com/vtapi/v2/file/scan"
virus_total_get_report_url = "https://www.virustotal.com/vtapi/v2/file/report"
virus_total_api_key = os.getenv("Virus_Total_Api_Key")

FILE_WAITING_IN_QUEUE_CODE = -2

def scan_file(file_path):
    scan_id = upload_file(file_path)
    while True:
        report = get_report(scan_id)
        if "response_code" in report and report["response_code"] == FILE_WAITING_IN_QUEUE_CODE:
            time.sleep(10)
            continue
        elif "positives" in report:
            return report["positives"]


def upload_file(file_path):
    params = {'apikey': virus_total_api_key}
    files = {'file': (file_path, open(file_path, 'rb'))} 
    response = requests.post(virus_total_api_scan_url, files=files, params=params)
    response = response.json()
    return response["scan_id"]


def get_report(scan_id):
    params = {'apikey': virus_total_api_key, 'resource': scan_id}
    response = requests.get(virus_total_get_report_url, params=params)

    if not response:
        raise Exception("Unexpected error in response")
    
    if response.status_code == 204:
        response = {"response_code":FILE_WAITING_IN_QUEUE_CODE} 
        return response
    else:
        return response.json()


def get_all_files_from_folder(folder_path):
    files_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list

