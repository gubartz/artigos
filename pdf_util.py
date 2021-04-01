from collections import Counter

import fitz
from ftfy import fix_text


class PDFUtil:

    def __init__(self, pdf_file):
        self.pdf_file = fitz.open(pdf_file)
        self.spans = []
        self.lines = []
        self.font_count_usage = []
        self.font_size_count_usage = []
        self.most_frequent_font = ''
        self.most_frequent_font_size = 0

    def get_text2(self):
        full_text = ''
        for page in self.pdf_file:
            full_text += fix_text(page.get_text(), fix_latin_ligatures=True)

        return full_text

    def get_text(self):
        spans = self.get_text_spans()

        full_text = ''

        # for span in spans:
        #     full_text += fix_text(span['text'], fix_latin_ligatures=True) + ' '

        for line in self.lines:
            for span in line['spans']:
                full_text += fix_text(span['text'], fix_latin_ligatures=True)
            full_text += "\n"

        return full_text

    def get_text_spans(self):
        if self.spans:
            return self.spans

        ordered_blocks = []

        for page in self.pdf_file:
            page_blocks = []
            block_dicts = page.getText("dict")
            for block in block_dicts["blocks"]:
                if block["type"] == 0:
                    page_blocks.append(block)

            # Natural reading order
            page_blocks = sorted(page_blocks, key=lambda k: (k['bbox'][1], k['bbox'][0]))
            ordered_blocks.extend(page_blocks)

        for block in ordered_blocks:
            for line in block["lines"]:
                self.lines.append(line)
                for span in line["spans"]:
                    self.spans.append(span)

        return self.spans

    def is_most_frequent_font(self, font):
        if not self.font_count_usage:
            self.__most_frequent_fonts()

        if self.most_frequent_font == font:
            return True

        return False

    def is_most_frequent_font_size(self, size):
        if not self.font_size_count_usage:
            self.__most_used_font_sizes()

        if self.most_frequent_font_size == size:
            return True

        return False

    def __most_frequent_fonts(self):
        font_count_usage = []

        if self.font_count_usage:
            return self.font_count_usage

        for span in self.get_text_spans():
            font_count_usage.append(span['font'])

        self.font_count_usage = dict(Counter(font_count_usage))

        self.font_count_usage = {k: v for k, v in
                                 sorted(self.font_count_usage.items(), key=lambda item: item[1], reverse=True)}

        self.most_frequent_font = next(iter(self.font_count_usage))

        return self.font_count_usage

    def __most_used_font_sizes(self):
        font_size_count_usage = []

        if self.font_size_count_usage:
            return self.font_size_count_usage

        for span in self.get_text_spans():
            font_size_count_usage.append(span['size'])

        self.font_size_count_usage = dict(Counter(font_size_count_usage))

        self.font_size_count_usage = {k: v for k, v in
                                      sorted(self.font_size_count_usage.items(), key=lambda item: item[1],
                                             reverse=True)}

        self.most_frequent_font_size = next(iter(self.font_size_count_usage))

        return self.font_size_count_usage

    def get_body_text(self):
        self.__most_used_font_sizes()
        spans = self.get_text_spans()
        body_text = ''

        for line in self.lines:
            for span in line['spans']:
                if self.is_most_frequent_font(span['font']) and self.is_most_frequent_font_size(span['size']):
                    body_text += fix_text(span['text'], fix_latin_ligatures=True)
            body_text += "\n"

        return body_text
