import unittest
from unittest.mock import patch, Mock, MagicMock
from bs4 import BeautifulSoup
import pandas as pd
import tempfile
import os
from pydub import AudioSegment

# Assuming the functions are in a module named `app`
from app import (
    fetch_webpage,
    translate_text,
    save_to_csv,
    has_chinese,
    read_aloud,
    remove_bracketed_numbers,
    get_sentences_from_html,
    translate_and_save,
    on_click_translate,
    on_click_read
)

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

    def test_has_chinese(self):
        self.assertTrue(has_chinese('测试'))
        self.assertFalse(has_chinese('test'))
        self.assertTrue(has_chinese('The company has over 500 employees and more than 493 patents.'))

 

    # @patch('app.gTTS.save')
    # @patch('app.AudioSegment.from_mp3')
    # def test_read_aloud(self, mock_from_mp3, mock_save):
    #     mock_audio_segment = MagicMock()
    #     mock_from_mp3.return_value = mock_audio_segment
    #     text = 'This is a test. 这是一个测试。'

    #     read_aloud(text)

    #     self.assertEqual(mock_save.call_count, 2)
    #     self.assertEqual(mock_from_mp3.call_count, 2)
    #     mock_audio_segment.export.assert_called_once()
    #     mock_audio_segment.__add__.assert_called_once_with(mock_audio_segment)

    def test_remove_bracketed_numbers(self):
        text = "This is a test[1]."
        result = remove_bracketed_numbers(text)
        self.assertEqual(result, "This is a test.")

    def test_get_sentences_from_html(self):
        html_content = '<html><body><p>This is a test. 这是一个测试。</p></body></html>'
        result = get_sentences_from_html(html_content)
        expected = ['This is a test.', '这是一个测试。']
        self.assertEqual(result, expected)

    @patch('app.translate_text')
    @patch('app.save_to_csv')
    def test_translate_and_save(self, mock_save_to_csv, mock_translate_text):
        mock_translate_text.side_effect = ['This is a test.', 'This is a test.']
        sentences = ['这是一个测试。']
        result = translate_and_save(sentences)
        self.assertEqual(result, [('这是一个测试。', 'This is a test.')])
        mock_save_to_csv.assert_called_once_with([('这是一个测试。', 'This is a test.')])

if __name__ == '__main__':
    unittest.main(exit=False)

