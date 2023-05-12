from bs4 import BeautifulSoup
from bs4 import PageElement
from datetime import datetime
import re
import logging


class RadaStenoParser:
    __items: []

    def parse_page_html(self, html):
        self.__items = []

        soup = BeautifulSoup(html, "html.parser")
        container = soup.find('div', class_="item_content")

        start_time = None
        time_code = 0
        time_code_previous = 0

        chairman = None
        speaker = None

        item_raw_text = ''
        item_text = ''
        item_speaker = ''
        item_tags = []
        item_concatenation_with = '\n'

        for p in container.find_all('p'):
            skip_text = False

            if self.__has_no_content(p):
                continue

            ext = str(p.extract())
            raw_text = self.__replace_lang_tags(ext.replace('\n', ' ') if ext != '' else '')

            text, tags = self.__clear_and_get_special_tags(raw_text)
            text, has_chairman_prefix = self.__replace_chairman(text)

            # name

            name = self.__get_name(raw_text, chairman)

            if name is not False:
                if self.__is_centered_text(p):
                    chairman = name

                speaker = name

                if not has_chairman_prefix:
                    skip_text = True

                if item_speaker != '' and item_speaker != speaker:
                    tags.append('multispeaker')

            if '' == item_speaker and speaker is not None:
                item_speaker = speaker

            # time

            time = self.__is_time_format(text)

            if time:
                skip_text = True

                if start_time is None:
                    start_time = time

                time_code_previous = time_code
                time_code = (time - start_time).total_seconds()

            started = start_time is not None and speaker is not None

            if started and time and time_code > 0:
                item = self.__get_item(
                    time_code_previous,
                    time_code,
                    item_speaker,
                    item_raw_text,
                    item_text,
                    list(set(item_tags))
                )

                self.__items.append(item)

                item_raw_text = ''
                item_text = ''
                item_speaker = ''
                item_tags = []

            if started and not skip_text:
                item_raw_text += (item_concatenation_with if item_raw_text != '' and raw_text != '' else '') + raw_text
                item_text += (item_concatenation_with if item_text != '' and text.strip() != '' else '') + text.strip()
                item_tags += tags

        item = self.__get_item(
            time_code_previous,
            time_code,
            item_speaker,
            item_raw_text,
            item_text,
            list(set(item_tags))
        )

        self.__items.append(item)

    def get_results(self):
        return self.__items

    def __has_no_content(self, e: PageElement) -> bool:
        return (len(e.text.strip()) == 0) \
            or (e.contents[0] == '\xa0')

    def __is_centered_text(self, e: PageElement) -> bool:
        return 'align' in e.attrs and e.attrs['align'] == 'center'

    def __is_time_format(self, text: str):
        try:
            return datetime.strptime(text, '%H:%M:%S')
        except ValueError:
            return False

    def __get_name(self, text: str, chairman_name: str):
        names = re.findall('([А-ЯІЇЄҐ\']* [А-ЯІЇЄҐ\']\.[А-ЯІЇЄҐ\']\.)', text)

        if len(names):
            return names[0]

        if text[:11] == 'ГОЛОВУЮЧИЙ.':
            return chairman_name

        return False

    def __replace_chairman(self, text: str):
        if text[:11] == 'ГОЛОВУЮЧИЙ.':
            return text[11:], True

        return text, False

    def __clear_and_get_special_tags(self, html: str):
        p = re.compile(r'<i.*?\/i>')
        tags_html = p.findall(html)

        html = p.sub('', html)
        tags = []

        for tag_html in tags_html:
            if 'Оплески' in tag_html:
                tags.append('applause')
            if 'Шум' in tag_html:
                tags.append('noise')
            if 'Гімн' in tag_html:
                tags.append('hymn')
            if 'перерви' in tag_html:
                tags.append('has_break')

        return html, tags

    def __replace_lang_tags(self, html: str):
        soup = BeautifulSoup(html, "html.parser")

        p_tag = soup.find('p')
        span_tags = soup.find_all("span")

        for span in span_tags:
            replace_with = ' '

            if 'lang' in span.attrs:
                lang = span.attrs['lang']

                # Make a new tag
                new_tag = soup.new_tag("", lang)
                new_tag.string = span.text

                replace_with = span.text

            span.replace_with(replace_with)

        return p_tag.decode_contents()

    def __get_item(self, start, end, speaker, raw_text, text, tags):
        return {
            'time_start': start,
            'time_end': end,
            'length': end - start,
            'speaker': speaker,
            'raw': raw_text,
            'text': text,
            'tags': tags
        }