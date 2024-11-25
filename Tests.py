# Importeer de benodigde modules voor testen
import unittest
from unittest.mock import patch, MagicMock
from MainApp import MainApp, AdminApp, Login, USER_FILE, PLUGIN_FILE, USER_PLUGINS_FILE

# User Stories Test Cases

class TestPluginMarketplace(unittest.TestCase):
    # Testgeval voor Jan's User Story
    @patch('MainApp.MainApp.read_csv')
    @patch('MainApp.MainApp.write_csv')
    def test_jan_buy_and_rent_plugin(self, mock_write_csv, mock_read_csv):
        # Mock de beschikbare plug-ins
        mock_read_csv.side_effect = [
            [
                {'plugin_name': 'Reverb', 'manufacturer': 'AIR', 'license_type': 'Subscription', 'price': '5'},
                {'plugin_name': 'Chorus', 'manufacturer': 'AIR', 'license_type': 'One Time Payment', 'price': '15'}
            ],
            []
        ]
        app = MainApp(user='Jan')
        app.show_available_plugins()

        # Controleer of Jan een One Time Payment plug-in kan kopen
        plugin = {'plugin_name': 'Chorus', 'manufacturer': 'AIR', 'license_type': 'One Time Payment', 'price': '15'}
        app.buy_plugin(plugin)
        mock_write_csv.assert_called_with(USER_PLUGINS_FILE, [{'username': 'Jan', 'plugin_name': 'Chorus'}], fieldnames=['username', 'plugin_name'])

        # Controleer of Jan een Subscription plug-in kan huren
        plugin = {'plugin_name': 'Reverb', 'manufacturer': 'AIR', 'license_type': 'Subscription', 'price': '5'}
        app.buy_plugin(plugin)
        mock_write_csv.assert_called_with(USER_PLUGINS_FILE, [{'username': 'Jan', 'plugin_name': 'Chorus'}, {'username': 'Jan', 'plugin_name': 'Reverb'}], fieldnames=['username', 'plugin_name'])

    # Testgeval voor Anna's User Story
    @patch('MainApp.MainApp.read_csv')
    @patch('MainApp.MainApp.write_csv')
    def test_anna_manage_plugins(self, mock_write_csv, mock_read_csv):
        # Mock de plug-ins die Anna bezit en de beschikbare plug-ins
        mock_read_csv.side_effect = [
            [
                {'plugin_name': 'Delay', 'manufacturer': 'AIR', 'license_type': 'Subscription', 'price': '5'},
                {'plugin_name': 'Compressor', 'manufacturer': 'AIR', 'license_type': 'One Time Payment', 'price': '20'}
            ],
            [
                {'username': 'Anna', 'plugin_name': 'Delay'},
                {'username': 'Anna', 'plugin_name': 'Compressor'}
            ],
            # Beschikbare plug-ins na annulering
            [
                {'plugin_name': 'Reverb', 'manufacturer': 'AIR', 'license_type': 'Subscription', 'price': '5'},
                {'plugin_name': 'EQ', 'manufacturer': 'AIR', 'license_type': 'One Time Payment', 'price': '10'}
            ],
            # Plug-ins die Anna bezit na annulering van Delay
            [
                {'username': 'Anna', 'plugin_name': 'Compressor'}
            ],
            # Plug-ins die Anna bezit na aankoop van nieuwe plug-ins
            [
                {'username': 'Anna', 'plugin_name': 'Compressor'},
                {'username': 'Anna', 'plugin_name': 'Reverb'},
                {'username': 'Anna', 'plugin_name': 'EQ'}
            ]
        ]
        app = MainApp(user='Anna')
        app.show_owned_plugins()

        # Anna besluit de Delay plug-in te annuleren
        plugin = {'plugin_name': 'Delay', 'manufacturer': 'AIR', 'license_type': 'Subscription', 'price': '5'}
        app.cancel_license(plugin)
        mock_write_csv.assert_called_with(USER_PLUGINS_FILE, [{'username': 'Anna', 'plugin_name': 'Compressor'}], fieldnames=['username', 'plugin_name'])

        app.show_available_plugins()

        # Anna koopt en huurt nieuwe plug-ins
        plugin = {'plugin_name': 'Reverb', 'manufacturer': 'AIR', 'license_type': 'Subscription', 'price': '5'}
        app.buy_plugin(plugin)
        mock_write_csv.assert_called_with(USER_PLUGINS_FILE, [{'username': 'Anna', 'plugin_name': 'Compressor'}, {'username': 'Anna', 'plugin_name': 'Reverb'}], fieldnames=['username', 'plugin_name'])

        plugin = {'plugin_name': 'EQ', 'manufacturer': 'AIR', 'license_type': 'One Time Payment', 'price': '10'}
        app.buy_plugin(plugin)
        mock_write_csv.assert_called_with(USER_PLUGINS_FILE, [{'username': 'Anna', 'plugin_name': 'Compressor'}, {'username': 'Anna', 'plugin_name': 'Reverb'}, {'username': 'Anna', 'plugin_name': 'EQ'}], fieldnames=['username', 'plugin_name'])

    # Testgeval voor Piet's User Story
    @patch('MainApp.AdminApp.read_csv')
    @patch('MainApp.AdminApp.write_csv')
    def test_piet_add_plugins(self, mock_write_csv, mock_read_csv):
        # Mock de bestaande plug-ins op het platform
        mock_read_csv.side_effect = [
            []
        ]
        app = AdminApp(user='Piet')

        # Piet voegt de Bitcrusher en EQ plug-ins toe
        app.entry_name = MagicMock()
        app.entry_license = MagicMock()
        app.entry_price = MagicMock()

        app.entry_name.get.side_effect = ['Bitcrusher', 'EQ']
        app.entry_license.get.side_effect = ['Subscription', 'One Time Payment']
        app.entry_price.get.side_effect = ['5', '15']

        # Bitcrusher toevoegen
        app.add_plugin()
        mock_write_csv.assert_called_with(PLUGIN_FILE, [{'plugin_name': 'Bitcrusher', 'manufacturer': 'Piet', 'license_type': 'Subscription', 'price': '5'}], fieldnames=['plugin_name', 'manufacturer', 'license_type', 'price'])

        # EQ toevoegen
        app.add_plugin()
        mock_write_csv.assert_called_with(PLUGIN_FILE, [{'plugin_name': 'Bitcrusher', 'manufacturer': 'Piet', 'license_type': 'Subscription', 'price': '5'}, {'plugin_name': 'EQ', 'manufacturer': 'Piet', 'license_type': 'One Time Payment', 'price': '15'}], fieldnames=['plugin_name', 'manufacturer', 'license_type', 'price'])

        # Mock het lezen van de beschikbare plug-ins om te zien of ze vermeld staan
        mock_read_csv.side_effect = lambda *args, **kwargs: [
            {'plugin_name': 'Bitcrusher', 'manufacturer': 'Piet', 'license_type': 'Subscription', 'price': '5'},
            {'plugin_name': 'EQ', 'manufacturer': 'Piet', 'license_type': 'One Time Payment', 'price': '15'}
        ]
        app.show_available_plugins()
        self.assertGreaterEqual(mock_read_csv.call_count, 2)  # Verifieer dat plug-ins worden gelezen uit het bestand

if __name__ == '__main__':
    unittest.main()
