import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from winner.winner_routes import winner_bp, get_rand_player, get_player_image, get_player_stats, compare_wins
import pandas as pd

class TestWinnerRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(winner_bp)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('winner.winner_routes.statsapi.lookup_team')
    @patch('winner.winner_routes.team_names', new_callable=dict)
    def test_team_names_loading(self, mock_team_names, mock_lookup_team):
        mock_lookup_team.return_value = [{'name': 'Team A'}]
        mock_team_names.update({108: 'Team A'})
        self.assertEqual(mock_team_names, {108: 'Team A'})

    def test_index(self):
        with patch('winner.winner_routes.render_template') as mock_render_template:
            mock_render_template.return_value = 'Render Content'
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Render Content', response.data)

    @patch('winner.winner_routes.get_rand_player')
    @patch('winner.winner_routes.get_player_stats')
    def test_start_game(self, mock_get_player_stats, mock_get_rand_player):
        mock_get_player_stats.side_effect = [25, 25]
        mock_get_rand_player.side_effect = [{'fullName': 'Player A', 'id': 1}, {'fullName': 'Player B', 'id': 2}]

        response = self.client.get('/start_game')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['playerA'], 'Player A')
        self.assertEqual(data['playerB'], 'Player B')
        self.assertEqual(data['winsA'], 25)
        self.assertEqual(data['winsB'], 25)

    @patch('winner.winner_routes.statsapi.lookup_player')
    @patch('winner.winner_routes.get_player_image')
    def test_player_images(self, mock_get_player_image, mock_lookup_player):
        mock_lookup_player.side_effect = [
            [{'fullName': 'Player A', 'currentTeam': {'id': 108}}],
            [{'fullName': 'Player B', 'currentTeam': {'id': 109}}]
        ]
        mock_get_player_image.side_effect = ['/images/playerA.jpg', '/images/playerB.jpg']

        response = self.client.post('/player_images', json={
            'playerA': 'Player A',
            'playerB': 'Player B'
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['playerA_img'], '/images/playerA.jpg')
        self.assertEqual(data['playerB_img'], '/images/playerB.jpg')

    @patch('winner.winner_routes.get_player_stats')
    @patch('winner.winner_routes.compare_wins')
    @patch('winner.winner_routes.statsapi.lookup_player')
    def test_check_answer(self, mock_lookup_player, mock_compare_wins, mock_get_player_stats):
        mock_lookup_player.side_effect = [
            [{'id': 1, 'fullName': 'Player A'}],
            [{'id': 2, 'fullName': 'Player B'}]
        ]
        mock_get_player_stats.side_effect = [30, 25]
        mock_compare_wins.return_value = 'Player A'

        response = self.client.post('/check_answer', json={
            'playerA': 'Player A',
            'playerB': 'Player B',
            'user_input': 'higher'
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['correct'])
        self.assertEqual(data['streak'], 1)
        self.assertEqual(data['winsA'], '30')
        self.assertEqual(data['winsB'], '25')

    @patch('winner.winner_routes.statsapi.lookup_player')
    @patch('winner.winner_routes.get_player_stats')
    @patch('winner.winner_routes.get_rand_player')
    def test_next_question(self, mock_get_rand_player, mock_get_player_stats, mock_lookup_player):
        # Mock setup
        mock_get_player_stats.side_effect = [30, 25]
        mock_get_rand_player.side_effect = [{'fullName': 'Player C', 'id': 3}, {'fullName': 'Player A', 'id': 1}]
        mock_lookup_player.side_effect = [
            [{'id': 1, 'fullName': 'Player A'}],  # For 'Player A'
            [{'id': 3, 'fullName': 'Player C'}]   # For 'Player C'
        ]
    
        response = self.client.post('/next_question', json={
            'previous_playerA': 'Player A'
        })

        

        data = response.get_json()

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['newPlayerA'], 'Player C')
        self.assertEqual(data['newPlayerB'], 'Player A')
        self.assertEqual(data['new_winsA'], 30)
        self.assertEqual(data['new_winsB'], 25)

    @patch('winner.winner_routes.streak', new=5)
    def test_end_game(self):
        response = self.client.post('/end_game')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['final_streak'], 5)

if __name__ == '__main__':
    unittest.main()