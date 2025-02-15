# apkizer coded by ko2sec

import requests
import bs4
import argparse
from requests.models import Response
import cloudscraper
import os
import zipfile


def main():
    parser = argparse.ArgumentParser(
        description='Download all versions of an Android mobile application from apkpure.com')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-p', required=True, metavar="packagename", help="example: com.twitter.android")
    required.add_argument('--first', required=False, metavar="first", default=True, help="example: true")
    required.add_argument('--apk', required=False, metavar="apk", default=True, help="example: true")
    required.add_argument('--out', required=False, metavar="out", default='.', help="example: /output")
    args = parser.parse_args()

    scraper = cloudscraper.create_scraper(delay=10)
    base_url = "https://apkpure.com"
    package_name = args.p
    first = args.first
    apk = args.apk
    out = args.out
    package_url = ""
    download_version_list = []
    response = scraper.get("https://apkpure.com/search?q=" + package_name).text

    soup = bs4.BeautifulSoup(response, "html.parser")
    a_elements = soup.find_all("a")

    for element in a_elements:
        # print(element.attrs["href"])
        if "href" in element.attrs and element.attrs["href"] != None and package_name in element.attrs["href"]:
            if "/" in element.attrs["href"] and element.attrs["href"].split("/")[-1] == package_name:
                package_url = element.attrs["href"]

    if package_url == "":
        if "Cloudflare Ray ID" in response:
            print("Cloudflare protection could not be bypassed, trying again..")
            main()
        else:
            print("Package not found!")

        return

    """
    Here is full URL correlated with package name.
    """

    response = scraper.get(base_url + package_url + "/versions").text
    soup = bs4.BeautifulSoup(response, "html.parser")

    versions_elements_div = soup.find("ul", attrs={"class": "ver-wrap"})
    versions_elements_li = versions_elements_div.findAll("li", recursive=False)

    exist_apk = False
    exist_xapk = False
    for list_item in versions_elements_li:
        href = list_item.find("a").attrs["href"]
        exist_apk = exist_apk or "-APK" in href
        exist_xapk = exist_xapk or "-XAPK" in href
        download_version_list.append(href)

    """
    Make a list of download pages.
    """

    def download_apk(download_page):
        soup = bs4.BeautifulSoup(download_page, "html.parser")
        # download_link = soup.find("iframe", {"id": "iframe_download"}).attrs["src"]
        # filename = soup.find("span", {"class": "file"}).text.rsplit(' ', 2)[0].replace(" ", "_").lower()
        
        download_link = soup.find("a", {"id": "download_link"}).attrs["href"]

        ext = ".apk"
        if "/XAPK/" in download_link:
            ext = ".xapk"

        body = soup.find("body")
        filename = body.attrs["data-dt-pkg"] + "_" + body.attrs["data-dt-version"] + ext
        current_directory = os.getcwd()
        # final_directory = os.path.join(out, package_name)
        final_directory = out

        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        filename = os.path.join(final_directory, filename)
        open('filename.txt', 'w').write(filename)
        print(filename + " exists: " + str(os.path.exists(filename)))
        if os.path.exists(filename) and zipfile.ZipFile(filename).testzip() is None:
            print("File already exists!")
            return

        if os.path.exists(filename):
            os.remove(filename)
        print(filename + " is downloading, please wait..")
        file = scraper.get(download_link)
        open(filename, "wb").write(file.content)

    for apk_url in download_version_list:
        print(apk_url)
        if apk and exist_apk and "-APK" not in apk_url:
            continue

        download_page = scraper.get(base_url + apk_url).text
        if "Download Variant" in download_page:
            """
            There are sometimes APK variants in terms of architecture,
            we need to analyze it before getting download link.
            Getting first variant for now.
            """
            soup = bs4.BeautifulSoup(download_page, "html.parser")
            apk_url = soup.find("div", {"class": "table-cell down"}).find("a").attrs["href"]
            print(base_url + apk_url)
            download_page = scraper.get(base_url + apk_url).text
        download_apk(download_page)
        if first:
            break
    print("All APK's are downloaded!")


def banner():
    print("""

               _     _
              | |   (_)
  __ _  _ __  | | __ _  ____ ___  _ __
 / _` || '_ \ | |/ /| ||_  // _ \| '__|
| (_| || |_) ||   < | | / /|  __/| |
 \__,_|| .__/ |_|\_\|_|/___|\___||_|
       | |
       |_|
                    by ko2sec, v1.0
    """)
    main()


banner()
