'''

    Bluecoat SiteReview Checker (CLI) 
    from https://github.com/PoorBillionaire/sitereview

    Slightly changed; reads a site list from a textfile
        site list : "sitelist.lst"
    Outputs in CSV format on screen

    2018 - Koen Van Impe

'''

from __future__ import print_function

from argparse import ArgumentParser
from bs4 import BeautifulSoup
import json
import requests
import sys

import urllib2
import time
from socket import timeout
import socket

class SiteReview(object):
    def __init__(self):
        self.baseurl = "https://sitereview.bluecoat.com/resource/lookup"
        self.headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

    def sitereview(self, url):
        payload = {"url": url, "captcha":""}
        
        try:
            self.req = requests.post(
                self.baseurl,
                headers=self.headers,
                data=json.dumps(payload),
            )
        except requests.ConnectionError:
            sys.exit("[-] ConnectionError: " \
                     "A connection error occurred")

        return json.loads(self.req.content.decode("UTF-8"))

    def check_response(self, response):
        if self.req.status_code != 200:
            sys.exit("[-] HTTP {} returned".format(req.status_code))
        else:
            self.category = response["categorization"][0]["name"]
            self.date = response["translatedRateDates"][0]["text"][0:35]
            self.url = response["url"]


def printcsv(url, ip, site_live, status_code, date, category):
    print("%s,%s,%s,%s,%s,%s" % (url, ip, site_live, status_code, date, category))    


def main(url):
    category = ""
    date = ""
    site_live = False
    status_code = 0
    ip = ""

    try:
        ip = socket.gethostbyname(url)
        try:
            response = urllib2.urlopen("http://" + url, timeout=5)
            status_code = response.getcode()
            s = SiteReview()
            
            response = s.sitereview(url)
            s.check_response(response)
            date = s.date
            category = s.category
            site_live = True
        except urllib2.URLError as err:
            category = err.reason
        except urllib2.HTTPError as err:
            if err.code == 302:
                category = "HTTP-302"
        except:
            category = "Unknown error"
        printcsv(url, ip, site_live, status_code, date, category)

    except socket.gaierror:
        printcsv(url, ip, site_live, status_code, date, "No DNS")
        
    if not url.startswith("www"):
        main("www."+url)

if __name__ == "__main__":
    file = open("sitelist.lst", "r")
    for site in file:
        site = site.rstrip()
        if site.startswith("http://"):
            site = site[7:]
        if site.startswith("https://"):
            site = site[8:]
        main(site)
        time.sleep(5)
    file.close()