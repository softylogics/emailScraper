import re
from collections import deque
from urllib.parse import urlsplit

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from tkinter import filedialog as fd


def simpleSite(original_url):
    unscraped = deque([original_url])

    scraped = set()

    emails = set()

    while len(unscraped):
        url = unscraped.popleft()
        scraped.add(url)

        parts = urlsplit(url)

        base_url = "{0.scheme}://{0.netloc}".format(parts)
        if '/' in parts.path:
            path = url[:url.rfind('/') + 1]
        else:
            path = url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'

        }

        response = requests.get(url, headers=headers, timeout=10)

        # print(response.json())
        #        print("Content\n", response.content)
        #        print("Raw\n", response.raw)
        #        print("Enc\n", response.encoding)
        #        print("Head\n", response.headers)
        #        print("His\n", response.history)

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+.com", response.text, re.I))
        emails.update(new_emails)

        soup = BeautifulSoup(response.text, 'lxml')

        for anchor in soup.find_all("a"):
            if "href" in anchor.attrs:
                link = anchor.attrs["href"]
            else:
                link = ''

                if link.startswith('/'):
                    link = base_url + link

                elif not link.startswith('http'):
                    link = path + link

                if not link.endswith(".gz"):
                    if not link in unscraped and not link in scraped:
                        unscraped.append(link)
    # for email in emails:
    #    print(email)
    # df = pd.DataFrame(emails, columns=["Email"])
    # df.to_csv('email.csv', index=False)
    return emails


def JSSite(url):
    EMAIL_REGEX = r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+.com"

    # initiate an HTTP session
    session = HTMLSession()
    # get the HTTP Response
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'

    }

    r = session.get(url, headers=headers)
    # for JAVA-Script driven websites
    r.html.render(timeout=20)
    emails = []
    for re_match in re.finditer(EMAIL_REGEX, r.html.raw_html.decode()):
        emails.append(re_match.group())
        # print(re_match.group())
    return emails


if __name__ == '__main__':
    def callback():
        name = fd.askopenfilename()
        print(name)

    urls = []
    urlsForCsv = []
    file = open('urls.txt', "r")
    for line in file:
        urls.append(line)
    emails = []

    for url in urls:
        try:
            print("\nfinding for url ", url)
            print("Simple Crawling")
            simpleEmails = simpleSite(url)
            print("JS Crawling")
            JSEmails = JSSite(url)
        except:
            print("Some Error Occurred")
        for email in simpleEmails:
            if email not in emails:
                emails.append(email)
                urlsForCsv.append(url)

        for email in JSEmails:
            if email not in emails:
                emails.append(email)
                urlsForCsv.append(url)

        print("Emails are now ", len(emails), " in size")

    df = pd.DataFrame({'Emails': emails, 'URLs': urlsForCsv})

    df.to_csv('email.csv', index=False)
