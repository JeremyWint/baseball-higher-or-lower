import scrapy
import csv
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TeamSpider(scrapy.Spider):
    name = "teamspider"
    start_urls = ["https://www.baseball-reference.com"]
    def __init__(self, *args, **kwargs):

        # List to store team links
        self.currTeamLinks = []
    def start_requests(self):
        yield SeleniumRequest(url='https://www.baseballreference.com', callback=self.toTeams)
    def toTeams(self, response):
        driver = response.meta['driver']
        xpath_selector = '/html/body/div[3]/div[1]/div[2]/ul[1]/li[2]/a/@href'
        link = response.xpath(xpath_selector).get()
        if link:
            full_url = response.urljoin(link)
            yield scrapy.Request(
                url=full_url,
                callback=self.toPlayers
            )
    def toPlayers(self, response):
        for row in range(1, 64):
            link = response.xpath(f'//table//tr[{row}]/td[1]/a/@href').get()
            if link:
                full_url = response.urljoin(link)
                yield scrapy.Request(
                    url=full_url,
                    callback=self.toCurrTeam
                )
    def toCurrTeam(self, response):
        restLink = response.xpath('//table/tbody/tr[1]/td[1]/a/@href').get()
        teamName = response.xpath('//*[@id="meta"]/div[2]/h1/span[1]/text()').get()
        if restLink:
            full_url = response.urljoin(restLink)
            teamInfo = {'Team Name': teamName, 'Link': full_url}
            self.currTeamLinks.append(teamInfo)


    
    def closed(self, reason):
         with open('team_links.csv', mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['Team Name', 'Link']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for team in self.currTeamLinks:
                writer.writerow(team)


