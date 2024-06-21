# Import required libraries
import json
import time

import requests


class Acunetix:
    def __init__(self, apikey="1986ad8c0a5b3df4d7028d5f3c06e936ced0d74450ffb4b3888d55ce96c8150d5",
                 api_server="https://localhost:3443/api/v1"):
        self.api_server = api_server
        self.apikey = apikey
        self.headers = {'X-Auth': apikey, 'Content-Type': 'application/json'}
        self.full_scan_profile_id = "11111111-1111-1111-1111-111111111111"

    def cleanup(self, scan_id, target_id):
        # Delete the scan
        requests.delete(f"{self.api_server}/scans/{scan_id}", headers=self.headers, verify=False)
        # Delete the target
        requests.delete(f"{self.api_server}/targets/{target_id}", headers=self.headers, verify=False)

    def run_scan(self, target, description, profile_id):
        # Create the target
        request_body = {"address": target, "description": description, "type": "default", "criticality": 10}
        target_id_response = requests.post(f"{self.api_server}/targets/", json=request_body, headers=self.headers,
                                           verify=False)
        target_id = json.loads(target_id_response.content)["target_id"]
        # Create the scan
        scan_id = requests.post(f"{self.api_server}/scans", json=request_body, headers=self.headers, verify=False)
        # Trigger a scan on the target - scan ID is in the HTTP response headers
        request_body = {"profile_id": profile_id, "incremental": False,
                        "schedule": {"disable": False, "start_date": None, "time_sensitive": False},
                        "user_authorized_to_scan": "yes", "target_id": target_id}
        scan_id_response = requests.post(f"{self.api_server}/scans", json=request_body, headers=self.headers,
                                         verify=False)
        scan_id = scan_id_response.headers["Location"].replace("/api/v1/scans/", "")

        completed = False
        while not completed:
            scan_status_response = requests.get(f"{self.api_server}/scans/{scan_id}", headers=self.headers,
                                                verify=False)
            tmp_json = json.loads(scan_status_response.content)
            scan_status = tmp_json["current_session"]["status"]
            match scan_status:
                case "processing":
                    print("Scan Status: Processing - waiting 30 seconds...")
                case "scheduled":
                    print("Scan Status: Scheduled - waiting 30 seconds...")
                case "completed":
                    completed = True
                case _:
                    print("Invalid Scan Status: Aborting")
                    self.cleanup(scan_id, target_id)
                    exit()
            time.sleep(30)
        return scan_id, target_id

    def get_vulnerabilities(self, scan_id, target_id):
        scan_session_response = requests.get(f"{self.api_server}/scans/{scan_id}/results", headers=self.headers,
                                             verify=False)
        scan_session_id = json.loads(scan_session_response.content)["current_session"]["scan_session_id"]
        # Obtain the scan result ID
        scan_result_response = requests.get(f"{self.api_server}/scans/{scan_id}/results", headers=self.headers,
                                            verify=False)
        scan_result_id = json.loads(scan_result_response.content)["results"][0]["result_id"]
        # Obtain scan vulnerabilities
        scan_vulnerabilities_response = requests.get(
            f"{self.api_server}/scans/{scan_id}/results/{scan_result_id}/vulnerabilities", headers=self.headers,
            verify=False)

        report = f"""
        Target ID: {target_id}
        Scan ID: {scan_id}
        Scan Session ID: {scan_session_id}
        Scan Result ID: {scan_result_id}
        Scan Vulnerabilities Response: {scan_vulnerabilities_response.content}
       """
        print(report)


if __name__ == "__main__":
    acunetix = Acunetix()
    scan_id, target_id = acunetix.run_scan("http://example.com", "test", acunetix.full_scan_profile_id)
    acunetix.get_vulnerabilities(scan_id, target_id)
