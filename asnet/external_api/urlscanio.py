# import asyncio
# import csv
# import json
# import logging
# import os
# import pathlib
# import platform
# import re
# from pathlib import Path
#
# import aiofiles
# import aiohttp
#
# from utils import is_url_valid
#
# logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
#
#
# # def create_arg_parser():
# #     parser = argparse.ArgumentParser(
# #         prog="urlscan",
# #         description=(
# #             "Call URLScan.io's submission and result APIs to get information about "
# #             "a website. This tool requires an environment variable named "
# #             "URLSCAN_API_KEY to be set to your API key.\nOptionally, you may also set "
# #             "an environment variable called URLSCAN_DATA_DIR to specify where the "
# #             "screenshots and DOM should be downloaded. If not set, they will be downloaded "
# #             "in your current directory."
# #         ),
# #     )
# #     parser.add_argument(
# #         "-v", "--verbose",
# #         help=(
# #             "Determines how verbose the output of the command will be. There are three "
# #             "possible values: 0 (critical), 1 (info), and 2 (debug). The default value "
# #             "is set to 0 when no verbose flag is present. If a flag is added with no "
# #             "value specified, it is set to 1. Otherwise, it will simply use the value "
# #             "specified."
# #         ),
# #         choices=[0, 1, 2], default=0, nargs="?", const=1,
# #         type=int
# #     )
# #
# #     parser.add_argument(
# #         "-p", "--private",
# #         help="Submit the URL in private. Private searches are not shared with other users.",
# #         action="store_true"
# #     )
# #
# #     group = parser.add_mutually_exclusive_group(required=True)
# #     group.add_argument(
# #         "-b", "--batch-investigate",
# #         help=(
# #             "Investigates the URLs included in the specified file. Returns an output CSV "
# #             "containing report, DOM, and screenshot locations for each URL. Please keep "
# #             "your UrlScan.io rate limit in mind when running this."
# #         ),
# #         type=str
# #     )
# #     group.add_argument(
# #         "-i", "--investigate",
# #         help=(
# #             "Investigate the specified URL. Returns the report URL and the locations of the "
# #             "DOM and screenshots."
# #         ),
# #         type=str
# #     )
# #     group.add_argument(
# #         "-s", "--submit",
# #         help="Submit a scan request for the specified URL. Returns the corresponding UUID.",
# #         type=str
# #     )
# #     group.add_argument(
# #         "-r", "--retrieve",
# #         help=(
# #             "Retrieves the scan report for the provided UUID. Returns the report URL and the "
# #             "download locations for the DOM and screenshot."
# #         ),
# #         type=str
# #     )
# #     group.add_argument(
# #         "-q", "--search-query",
# #         help="Submit a search request for the given query.",
# #         type=str
# #     )
# #     group.add_argument(
# #         "--get-report",
# #         help=(
# #             "Get the scan report for the provided UUID, in JSON format."
# #         )
# #     )
# #
# #     return parser
#
#
# def validate_arguments(args):
#     uuid_validator = re.compile(
#         "^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
#     )
#
#     if (args.investigate and not is_url_valid(args.investigate)) or \
#             (args.submit and not is_url_valid(args.submit)):
#         raise ValueError(
#             "The URL provided does not contain the scheme (e.g. http:// or https://) "
#             "and/or a non-empty location (e.g. google.com)"
#         )
#     elif args.retrieve and not bool(uuid_validator.match(args.retrieve)):
#         raise ValueError("The UUID provided is incorrectly formatted")
#
#
# def create_data_dir(data_dir):
#     pathlib.Path(f"{data_dir}/screenshots").mkdir(exist_ok=True)
#     pathlib.Path(f"{data_dir}/doms").mkdir(exist_ok=True)
#
#
# def convert_int_to_logging_level(log_level):
#     mapping = {
#         0: logging.CRITICAL,
#         1: logging.INFO,
#         2: logging.DEBUG
#     }
#     return mapping[log_level]
#
#
# class UrlScan:
#     URLSCAN_API_URL = "https://urlscan.io/api/v1"
#     DEFAULT_PAUSE_TIME = 3
#     DEFAULT_MAX_ATTEMPTS = 15
#
#     def __init__(self, api_key, data_dir=Path.cwd(), log_level=0):
#         self.api_key = api_key
#         self.data_dir = data_dir
#         self.session = aiohttp.ClientSession(trust_env=True)
#         self.verbose = True
#         self.logger = logging.getLogger("urlscanio")
#         self.logger.setLevel(log_level)
#
#     async def __aenter__(self):
#         return self
#
#     async def __aexit__(self, *excinfo):
#         await self.session.close()
#
#     async def execute(self, method, url, headers=None, payload=None, params={}):
#         async with self.session.request(
#                 method=method,
#                 url=url,
#                 headers=headers,
#                 data=json.dumps(payload),
#                 params=params,
#                 ssl=False) as response:
#             self.logger.debug("%s request made to %s with %d response code", method, url, response.status)
#             return response.status, await response.read()
#
#     async def save_file(self, target_path, content):
#         self.logger.debug("Creating and saving %s", target_path)
#         async with aiofiles.open(target_path, "wb") as data:
#             await data.write(content)
#
#     async def submit_scan_request(self, url, private=False):
#         headers = {"Content-Type": "application/json", "API-Key": self.api_key}
#         payload = {"url": url} if private else {"url": url, "public": "on"}
#         status, response = await self.execute("POST", f"{self.URLSCAN_API_URL}/scan/", headers, payload)
#         if status == 429:
#             self.logger.critical("UrlScan did not accept scan request for %s, reason: too many requests", url)
#             return ""
#         body = json.loads(response)
#         if status >= 400:
#             self.logger.critical("UrlScan did not accept scan request for %s, reason: %s", url, body["description"])
#             return ""
#         return body["uuid"]
#
#     async def get_result_data(self, scan_uuid):
#         _, response = await self.execute("GET", f"{self.URLSCAN_API_URL}/result/{scan_uuid}")
#         body = json.loads(response)
#         return body
#
#     async def fetch_result(self, scan_uuid):
#         body = await self.get_result_data(scan_uuid)
#         return {
#             "scan_uuid": scan_uuid,
#             "report": body["task"]["reportURL"],
#             # "screenshot": await self.download_screenshot(body["task"]["screenshotURL"]),
#             "dom": await self.download_dom(scan_uuid, body["task"]["domURL"])
#         }
#
#     async def download_screenshot(self, screenshot_url):
#         self.logger.info("Downloading screenshot from %s", screenshot_url)
#         screenshot_name = screenshot_url.split("/")[-1]
#         screenshot_location = Path(f"{self.data_dir}/screenshots/{screenshot_name}")
#         status, response = await self.execute("GET", screenshot_url)
#         if status == 200:
#             await self.save_file(screenshot_location, response)
#             return str(screenshot_location)
#         self.logger.info("Could not download screenshot from %s, please visit URL for more info", screenshot_url)
#
#     async def download_dom(self, scan_uuid, dom_url):
#         self.logger.info("Downloading DOM from %s", dom_url)
#         dom_location = Path(f"{self.data_dir}/doms/{scan_uuid}.txt")
#         status, response = await self.execute("GET", dom_url)
#         if status == 200:
#             await self.save_file(dom_location, response)
#             return str(dom_location)
#         self.logger.info("Could not download DOM from %s, please visit URL for more info", dom_url)
#
#     async def investigate(self, url, private=False):
#         self.logger.critical("Starting investigation of %s, this may take a while...", url)
#         self.logger.debug("Default sleep time between attempts: %d, maximum number of attempts: %d",
#                           self.DEFAULT_PAUSE_TIME, self.DEFAULT_MAX_ATTEMPTS)
#
#         self.logger.info("Requesting scan for %s", url)
#         scan_uuid = await self.submit_scan_request(url, private)
#         if scan_uuid == "":
#             self.logger.critical("Failed to submit scan request for %s, cannot investigate", url)
#             return {}
#
#         self.logger.info("Request submitted for %s, attempting to retrieve scan %s", url, scan_uuid)
#
#         attempts = 0
#         await asyncio.sleep(self.DEFAULT_PAUSE_TIME)
#         while attempts < self.DEFAULT_MAX_ATTEMPTS:
#             self.logger.debug("Retrieving %s scan results %s, attempt #%d", url, scan_uuid, attempts)
#             try:
#                 return await self.fetch_result(scan_uuid)
#             except KeyError:
#                 attempts += 1
#                 await asyncio.sleep(self.DEFAULT_PAUSE_TIME)
#
#         self.logger.critical(
#             "Couldn't fetch report after %d tries. Please wait a few seconds and visit https://urlscan.io/result/%s/.",
#             attempts, scan_uuid
#         )
#         return {
#             "scan_uuid": scan_uuid
#         }
#
#     async def batch_investigate(self, urls_file, private=False):
#         output_file = open(f"{Path(urls_file).stem}.csv", "w")
#         output = csv.writer(output_file)
#         output.writerow(["url", "report", "screenshot", "dom"])
#
#         async with aiofiles.open(urls_file, "r") as urls_data:
#             coros = []
#             urls = []
#             async for url in urls_data:
#                 url = url.rstrip()
#                 urls.append(url)
#                 coros.append(asyncio.gather(self.investigate(url, private)))
#                 await asyncio.sleep(3)
#             all_results = await asyncio.gather(*coros)
#
#             for i, result in enumerate(all_results):
#                 result = result[0]
#
#                 report_url = result.get("report")
#                 if not report_url:
#                     scan_uuid = result.get("scan_uuid")
#                     if scan_uuid:
#                         report_url = f"https://urlscan.io/result/{scan_uuid}/"
#                 output.writerow([urls[i].rstrip(), report_url, result.get("screenshot"), result.get("dom")])
#
#             output_file.close()
#
#     async def search(self, query: str):
#         headers = {"API-Key": self.api_key}
#         params = {"q": query}
#         status, response = await self.execute("GET", f"{self.URLSCAN_API_URL}/search/", headers, params=params)
#         if status == 429:
#             self.logger.critical("UrlScan did not accept scan request for %s, reason: too many requests", query)
#             return ""
#         body = json.loads(response)
#         if status >= 400:
#             self.logger.critical("UrlScan did not accept scan request for %s, reason: %s", query, body["message"])
#             return ""
#         return body
#
#
# def urlscanio_main(url):
#     # parser = create_arg_parser()
#     # args = parser.parse_args()
#     # validate_arguments(args)
#
#     api_key = "97380a78-3631-40ff-9028-debfe85f7e87"  # os.environ["URLSCAN_API_KEY"]
#     data_dir = Path(os.getenv("URLSCAN_DATA_DIR", ""))
#     # log_level = convert_int_to_logging_level(args.verbose)
#
#     create_data_dir(data_dir)
#
#     # See https://github.com/iojw/socialscan/issues/13
#     if platform.system() == "Windows":
#         asyncio.set_event_loop_policy(policy=asyncio.WindowsSelectorEventLoopPolicy())
#
#     result = asyncio.run(execute2(url=url, api_key=api_key, data_dir=data_dir))
#     return result
#
#
# async def execute2(url, api_key, data_dir, log_level=2):
#     async with UrlScan(api_key=api_key, data_dir=data_dir, log_level=log_level) as url_scan:
#         investigation_result = await url_scan.investigate(url)
#         if investigation_result == {}:
#             print("\nInvestigation failed. Please try again later.")
#         else:
#             return investigation_result['report']
#             # if investigation_result.keys() >= {"report", "screenshot", "dom"}:
#             #     print(f"\nScan report URL:\t\t{investigation_result['report']}")
#             #     print(f"Screenshot download location:\t{investigation_result['screenshot']}")
#             #     print(f"DOM download location:\t\t{investigation_result['dom']}\n")
#
#     # elif args.retrieve:
#     #     retrieve_result = await url_scan.fetch_result(args.retrieve)
#     #     print(f"\nScan report URL:\t\t{retrieve_result['report']}")
#     #     print(f"Screenshot download location:\t{retrieve_result['screenshot']}")
#     #     print(f"DOM download location:\t\t{retrieve_result['dom']}\n")
#     #
#     # elif args.submit:
#     #     scan_uuid = await url_scan.submit_scan_request(args.submit, args.private)
#     #     if scan_uuid == "":
#     #         print(f"\nFailed to submit scan request for {args.submit}. Please try again later.\n")
#     #     else:
#     #         print(f"\nScan UUID:\t\t{scan_uuid}\n")
#     #
#     # elif args.batch_investigate:
#     #     await url_scan.batch_investigate(args.batch_investigate, args.private)
#     #     print(f"Investigation outputs written to {Path(args.batch_investigate).stem}.csv")
#     #
#     # elif args.search_query:
#     #     results = await url_scan.search(args.search_query)
#     #     if results:
#     #         print(json.dumps(results, indent=1, default=str))
#     #
#     # elif args.get_report:
#     #     results = await url_scan.get_result_data(args.get_report)
#     #     if results:
#     #         print(json.dumps(results, indent=1, default=str))
#
#
# async def execute(args, api_key, data_dir, log_level):
#     async with UrlScan(api_key=api_key, data_dir=data_dir, log_level=log_level) as url_scan:
#         if args.investigate:
#             investigation_result = await url_scan.investigate(args.investigate, args.private)
#             if investigation_result == {}:
#                 print("\nInvestigation failed. Please try again later.")
#             else:
#                 if investigation_result.keys() >= {"report", "screenshot", "dom"}:
#                     print(f"\nScan report URL:\t\t{investigation_result['report']}")
#                     print(f"Screenshot download location:\t{investigation_result['screenshot']}")
#                     print(f"DOM download location:\t\t{investigation_result['dom']}\n")
#
#         elif args.retrieve:
#             retrieve_result = await url_scan.fetch_result(args.retrieve)
#             print(f"\nScan report URL:\t\t{retrieve_result['report']}")
#             print(f"Screenshot download location:\t{retrieve_result['screenshot']}")
#             print(f"DOM download location:\t\t{retrieve_result['dom']}\n")
#
#         elif args.submit:
#             scan_uuid = await url_scan.submit_scan_request(args.submit, args.private)
#             if scan_uuid == "":
#                 print(f"\nFailed to submit scan request for {args.submit}. Please try again later.\n")
#             else:
#                 print(f"\nScan UUID:\t\t{scan_uuid}\n")
#
#         elif args.batch_investigate:
#             await url_scan.batch_investigate(args.batch_investigate, args.private)
#             print(f"Investigation outputs written to {Path(args.batch_investigate).stem}.csv")
#
#         elif args.search_query:
#             results = await url_scan.search(args.search_query)
#             if results:
#                 print(json.dumps(results, indent=1, default=str))
#
#         elif args.get_report:
#             results = await url_scan.get_result_data(args.get_report)
#             if results:
#                 print(json.dumps(results, indent=1, default=str))
#
#
# # if __name__ == "__main__":
# #     main()
