import scrapy
import csv
import os
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlencode
from scrapy.utils.log import configure_logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

class BackupSpider(scrapy.Spider):
    name="backupspider"
    def __init__(self, *args, **kwargs):
        """
        Initialize the spider, setting up the list for player data.
        """
        super(BackupSpider, self).__init__(*args, **kwargs)

        # List to store player information
        self.player_data = []

    def start_requests(self):
        """
        Read team links from a CSV file and yield SeleniumRequests for each URL.
        """
        urls = []

        # Open and read URLs from the CSV file
        with open('failed_urls.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                urls.append(row['failed_url'])

        # Yield a SeleniumRequest for each URL
        for url in urls:
            yield SeleniumRequest(
                url=url, 
                callback=self.teamPage, 

                # Wait time for Selenium to load the page
                wait_time=10)

    def teamPage(self, response):
        """
        Extract player links from the team list page and yield ScrapyRequests for each player.
        """

        # Iterate over possible rows in the table
        for row in range(1, 64):

            # Extract the relative URL for each player
            link = response.xpath(f'///*[@id="the40man"]/tbody/tr[{row}]/td[2]//a//@href').get()
            
            # Create absolute URL
            full_url = response.urljoin(link)
           
            # Yield a ScrapyRequest for the player's page
            yield scrapy.Request(
                url=full_url,
                callback=self.playerPage)

    def playerPage(self, response):
        """
        Extract player data from the player page and store it in the player_data list.
        """

        # Extract player name, image URL, and team from the page
        player_name = response.css('div#meta h1 span::text').get()
        image_url = response.xpath('//*[@id="meta"]/div[1]/img[1]/@src').get()
        image_url = response.urljoin(image_url)
        team = response.xpath('//p[contains(., "Team:")]/a/text()').get()
        
        # Create a dictionary with the extracted data
        player_stats = {'name': player_name, 'team': team, 'image_url': image_url}
        self.player_data.append(player_stats)
    
    def closed(self,reason):
        """
        Save player data and failed URLs to CSV files when the spider is closed.
        """

        # Save player data to an existing CSV file
        with open('player_image.csv', mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'team', 'image_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write player data rows
            for player in self.player_data:
                writer.writerow(player)

