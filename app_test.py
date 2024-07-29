import unittest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
import pandas as pd
import os


# Assuming the functions are in a module named `app`
from app  import fetch_webpage, translate_text, save_to_csv, read_aloud, get_paragraphs, translate_and_save

class TestWebpageTranslator(unittest.TestCase):

    @patch('app.requests.get')
    def test_fetch_webpage(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = 'test content'
        mock_get.return_value = mock_response

        url = 'http://example.com'
        result = fetch_webpage(url)
        self.assertEqual(result, 'test content')
        mock_get.assert_called_once_with(url)

    @patch('app.Translator.translate')
    def test_translate_text(self, mock_translate):
        mock_translate.return_value.text = '测试内容'
        text = 'test content'
        result = translate_text(text)
        self.assertEqual(result, '测试内容')
        mock_translate.assert_called_once_with(text, src='en', dest='zh-cn')

    def test_save_to_csv(self):
        data = [('test content', '测试内容')]
        df = save_to_csv(data, 'test.csv')
        self.assertTrue(os.path.exists('test.csv'))
        df_expected = pd.DataFrame(data, columns=['Original', 'Translated'])
        pd.testing.assert_frame_equal(df, df_expected)
        os.remove('test.csv')

    @patch('app.gTTS.save')
    @patch('app.os.system')
    def test_read_aloud(self, mock_system, mock_save):
        text = '测试内容'
        read_aloud(text)
        mock_save.assert_called_once_with("output.mp3")
        mock_system.assert_called_once_with("start output.mp3")

    def test_get_paragraphs(self):
        html_content = '<html><body><p>Test paragraph 1</p><p>Test paragraph 2</p></body></html>'
        result = get_paragraphs(html_content)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get_text(), 'Test paragraph 1')
        self.assertEqual(result[1].get_text(), 'Test paragraph 2')

    @patch('app.translate_text')
    @patch('app.save_to_csv')
    def test_translate_and_save(self, mock_save_to_csv, mock_translate_text):
        mock_translate_text.side_effect = ['测试段落 1', '测试段落 2']
        paragraphs = [BeautifulSoup('<p>Test paragraph 1</p>', 'html.parser').p,
                      BeautifulSoup('<p>Test paragraph 2</p>', 'html.parser').p]
        result = translate_and_save(paragraphs)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ('Test paragraph 1', '测试段落 1'))
        self.assertEqual(result[1], ('Test paragraph 2', '测试段落 2'))
        mock_save_to_csv.assert_called_once_with([('Test paragraph 1', '测试段落 1'), ('Test paragraph 2', '测试段落 2')])

if __name__ == '__main__':
    unittest.main()
