import unittest
from unittest.mock import patch, mock_open
from scrapy.http import HtmlResponse, Request
from scrapy_selenium import SeleniumRequest
import sys
import os

# Add the root directory of the project to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extract.spiders.backupspider import BackupSpider

class TestBackupSpider(unittest.TestCase):
    def setUp(self):
        self.spider = BackupSpider()

    def test_initialization(self):
        self.assertEqual(self.spider.player_data, [])

    @patch('extract.spiders.backupspider.open', new_callable=mock_open, read_data="failed_url\nhttp://example.com/team1\nhttp://example.com/team2")
    def test_start_requests(self, mock_file):
        # Simulate file reading by returning lines when the file object is iterated
        mock_file.return_value.__iter__.return_value = iter("failed_url\nhttp://example.com/team1\nhttp://example.com/team2".splitlines())

        requests = list(self.spider.start_requests())

        self.assertEqual(len(requests), 2)
        self.assertIsInstance(requests[0], SeleniumRequest)
        self.assertEqual(requests[0].url, 'http://example.com/team1')
        self.assertIsInstance(requests[1], SeleniumRequest)
        self.assertEqual(requests[1].url, 'http://example.com/team2')

        mock_file.assert_called_once_with('failed_urls.csv', 'r')

    def test_team_page(self):
        html_content = """
        <table id="the40man">
            <tbody>
                <tr>
                    <td></td>
                    <td><a href="/player1.html">Player 1</a></td>
                </tr>
                <tr>
                    <td></td>
                    <td><a href="/player2.html">Player 2</a></td>
                </tr>
            </tbody>
        </table>
        """
        response = HtmlResponse(url='http://example.com/team1', body=html_content, encoding='utf-8')
        requests = list(self.spider.teamPage(response))

        self.assertEqual(requests[0].url, 'http://example.com/player1.html')
        self.assertEqual(requests[1].url, 'http://example.com/player2.html')

    def test_player_page(self):
        html_content = """
        <div id="meta">
            <h1><span>Player Name</span></h1>
            <div><img src="/images/player.jpg" /></div>
        </div>
        <p>Team: <a>Team Name</a></p>
        """
        response = HtmlResponse(url='http://example.com/player1.html', body=html_content, encoding='utf-8')
        self.spider.playerPage(response)

        self.assertEqual(len(self.spider.player_data), 1)
        self.assertEqual(self.spider.player_data[0]['name'], 'Player Name')
        self.assertEqual(self.spider.player_data[0]['image_url'], 'http://example.com/images/player.jpg')
        self.assertEqual(self.spider.player_data[0]['team'], 'Team Name')

    @patch('extract.spiders.backupspider.open', new_callable=mock_open)
    def test_closed(self, mock_file):
        self.spider.player_data = [
            {'name': 'Player 1', 'team': 'Team 1', 'image_url': 'http://example.com/player1.jpg'},
            {'name': 'Player 2', 'team': 'Team 2', 'image_url': 'http://example.com/player2.jpg'}
        ]

        self.spider.closed('finished')
        mock_file.assert_any_call('player_image.csv', mode='a', newline='', encoding='utf-8')

        handle = mock_file()
        handle.write.assert_any_call('Player 1,Team 1,http://example.com/player1.jpg\r\n')
        handle.write.assert_any_call('Player 2,Team 2,http://example.com/player2.jpg\r\n')

if __name__ == '__main__':
    unittest.main()