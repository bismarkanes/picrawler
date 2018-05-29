"""
CRAWLER SCRIPT
"""

from __future__ import print_function

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import json
import datetime
import time
from lxml import html
import requests


def get_site_domain_url(url):
    """
    return protocol://basedomain
    """
    parsed = urlparse(url)
    return (parsed.scheme + '://' + parsed.hostname)


def get_site_content(url):
    """
    return text response of a page url
    """
    response = requests.get(url)
    return response.content


def get_company_links(htmlContent, out_links, basedomain):
    """
    get company links based on pages
    """
    htmlstr = html.fromstring(htmlContent)
    # id yw0
    links = htmlstr.xpath('//ul[contains(@id, "yw0")]//li[contains(@class, "page")]//a')

    for link in links:
        href = link.get('href')
        if href != '':
            out_links.append(basedomain + href)


def get_company_list(htmlContent, out_list, basedomain):
    """
    get company list on a page
    """
    htmlstr = html.fromstring(htmlContent)
    company_root_details = htmlstr.xpath('//div[contains(@class, "list-company")]')
    for company_detail in company_root_details:
        detail = html.tostring(company_detail)

        inner_company_detail = html.fromstring(detail)

        company_logo = inner_company_detail.xpath('//div[contains(@class, "com-card-info") and contains(@class, "clearfix")]//a[contains(@class, "href-company-div")]/img')
        if len(company_logo) > 0:
            company_logo = company_logo[0].get('data-original')
        else:
            company_logo = ''

        company_name = inner_company_detail.xpath('//div[contains(@class, "com-card-info") and contains(@class, "clearfix")]//h3')
        if len(company_name) > 0:
            company_name = company_name[0].text_content()
        else:
            company_name = ''

        company_href = inner_company_detail.xpath('//div[contains(@class, "com-card-info") and contains(@class, "clearfix")]//div/div/h3/a')
        if len(company_href) > 0:
            company_href = basedomain + company_href[0].get('href')
        else:
            company_href = ''

        company_industry = inner_company_detail.xpath('//div[contains(@class, "com-card-genre") and contains(@class, "clearfix")]//ul[contains(@class, "list-genre")]//li')

        alist = []
        for industry in company_industry:
            alist.append(industry.text_content().strip())

        company = {
            "company_name": company_name,
            "company_logo": company_logo,
            "url": company_href,
            "industry": ','.join(alist),
            "crawled_at": str(datetime.datetime.now().date())
        }

        out_list.append(company)


def getCompanyProfile(htmlContent, profile_list):
    """
    get company profile based on content of an url
    """
    htmlstr = html.fromstring(htmlContent)
    company_root_profile = htmlstr.xpath('//div[contains(@class, "page-company-detail")]//div[contains(@class, "item-com-detail")]')
    for company_profile in company_root_profile:
        detail = html.tostring(company_profile)

        inner_company_profile = html.fromstring(detail)

        company_logo = inner_company_profile.xpath('//div[contains(@class, "com-info") and contains(@class, "clearfix")]/img')
        if len(company_logo) > 0:
            company_logo = company_logo[0].get('src')
        else:
            company_logo = ''

        company_name = inner_company_profile.xpath('//div[contains(@class, "com-info") and contains(@class, "clearfix")]//h2/span')
        if len(company_name) > 0:
            company_name = company_name[0].text_content()
        else:
            company_name = ''

        company_description = inner_company_profile.xpath('//div[contains(@class, "com-info") and contains(@class, "clearfix")]//span[contains(@itemprop, "description")]')
        if len(company_description) > 0:
            company_description = company_description[0].text_content()
        else:
            company_description = ''

        company_address = inner_company_profile.xpath('//table[contains(@class, "tbl-com-detail") and contains(@class, "company_basic_info_table")]//div[contains(@itemprop, "address")]/span[contains(@itemprop, "streetAddress")]')
        if len(company_address) > 0:
            company_address = company_address[0].text_content()
        else:
            company_address = ''

        company_phone = inner_company_profile.xpath('//table[contains(@class, "tbl-com-detail") and contains(@class, "company_basic_info_table")]//td//span[contains(@itemprop, "telephone")]')
        if len(company_phone) > 0:
            company_phone = company_phone[0].text_content()
        else:
            company_phone = ''

        company_fax = inner_company_profile.xpath('//table[contains(@class, "tbl-com-detail") and contains(@class, "company_basic_info_table")]//td//span[contains(@itemprop, "faxNumber")]')
        if len(company_fax) > 0:
            company_fax = company_fax[0].text_content()
        else:
            company_fax = ''

        company_website = inner_company_profile.xpath('//table[contains(@class, "tbl-com-detail") and contains(@class, "company_basic_info_table")]//td//a[contains(@itemprop, "url")]')
        if len(company_website) > 0:
            company_website = company_website[0].get('href')
        else:
            company_website = ''

        business = inner_company_profile.xpath('//table[contains(@class, "tbl-com-detail") and contains(@class, "company_basic_info_table")]//th[contains(text(), "Business")]/following-sibling::td')
        if len(business) > 0:
            business = business[0].text_content().strip()
        else:
            business = ''

        business_form = inner_company_profile.xpath('//table[contains(@class, "tbl-com-detail") and contains(@class, "company_basic_info_table")]//th[contains(text(), "Business Form")]/following-sibling::td')
        if len(business_form) > 0:
            business_form = business_form[0].text_content().strip()
        else:
            business_form = ''

        industry = inner_company_profile.xpath('//div[contains(@class, "genre-com-detail") and contains(@class, "clearfix")]/ul/li/a')
        if len(industry) > 0:
            alist = []
            for in_item in industry:
                alist.append(in_item.text_content().strip())
                industry = ','.join(alist)
        else:
            industry = ''

        profile = {
            "company_name": company_name,
            "company_description": company_description,
            "company_logo": company_logo,
            "company_street_address": company_address,
            "company_phone": company_phone,
            "company_fax": company_fax,
            "company_website": company_website,
            "business_form": business_form,
            "business": business,
            "industry": industry
        }
        profile_list.append(profile)


def updateCompanyLinks(current_links, new_links):
    """
    Update company links
    """
    for new_link in new_links:
        if new_link not in current_links:
            current_links.append(new_link)


"""
MAIN PROGRAM STARTS HERE
"""

target_url = 'http://vtown.vn/en/category8/genre701.html'
USE_DELAY = False
company_list = []
company_links = []
company_profiles = []

base_domain_url = get_site_domain_url(target_url)
html_content = get_site_content(target_url)

# get company links
get_company_links(html_content, company_links, base_domain_url)

# get company list from the links
ncount=0
while ncount < len(company_links):
    if USE_DELAY:
        time.sleep(1)
    target_url = company_links[ncount]
    print('CompanyList: GET', target_url)
    html_content = get_site_content(target_url)
    get_company_list(html_content, company_list, base_domain_url)
    if len(company_links) > 0:
        cur_company_links = []
        get_company_links(html_content, cur_company_links, base_domain_url)
        updateCompanyLinks(company_links, cur_company_links)
    else:
        target_url = ''

    ncount += 1

# getting company profile
for company in company_list:
    url = company['url']
    print('CompanyProfile: GET', url)
    html_content = get_site_content(url)
    getCompanyProfile(html_content, company_profiles)
    if USE_DELAY:
        time.sleep(1)

# write to file
with open('./company_index.json', 'w') as outfile:
    json.dump(company_list, outfile)
print('writing to file company_index.json, DONE')

with open('./company_profiles.json', 'w') as outfile:
    json.dump(company_profiles, outfile)
print('writing to file company_profiles.json, DONE')
