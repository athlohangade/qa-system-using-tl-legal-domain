import pdftotext 
import re

class TextProcessingAndContextCreation :

    @classmethod
    def get_context_chunks(cls, file_name) :
        
        raw_text = cls._get_raw_text_from_pdf(file_name)
        first_page_number = cls._get_the_first_page_number(raw_text)
        if first_page_number == -1 :
            print("Error encountered")
            return []
        raw_text = raw_text[first_page_number:]
        cls._remove_header_of_first_page(raw_text)
        cls._delete_footer_notes(raw_text)
        cls._remove_captial_words(raw_text)
        text = cls._join_all_pages(raw_text)
        text = cls._split_the_text_on_bold_points(text)
        cls._filter_and_get_plain_text(text)
        # return text 
        contexts =  cls._get_the_contexts(text)
        return contexts

    @classmethod
    def _get_raw_text_from_pdf(cls, file_name) :

        with open(file_name, "rb") as f :
            pdf_text = pdftotext.PDF(f)
        
        raw_text = []
        for i in pdf_text :
            raw_text.append(str(i))
        return raw_text

    @classmethod
    def _get_the_first_page_number(cls, raw_text) :

        index = raw_text[0].split().index('ACT,')
        match_text_page_zero = " ".join(raw_text[0].split()[:index + 1])

        for i in range(1, len(raw_text)) :
            page_match_text = " ".join(raw_text[i].split()[:index + 1])
            if match_text_page_zero == page_match_text :
                return i
        return -1

    @classmethod
    def _remove_header_of_first_page(cls, raw_text) :

        temp = re.match(r"(.|\n)*?\[.*\]", raw_text[0])
        raw_text[0] = raw_text[0][temp.end():]

    @classmethod
    def _delete_footer_notes(cls, raw_text) :

        footer_regex = r"1\..*"
        for i in range(len(raw_text)) :
            temp = raw_text[i].split('\n')[:-2]
            for j in range(len(temp) - 1, -1, -1) :
                if re.match(footer_regex, temp[j]) is not None :
                    break
            if j != 0 :
                temp = temp[:j]
            raw_text[i] = "\n".join(temp)

    @classmethod
    def _remove_captial_words(cls, raw_text) :

        for i in range(len(raw_text)) :
            raw_text[i] = raw_text[i].split('\n')
            raw_text[i] = list(filter(lambda x: not (x.isupper()), raw_text[i]))
            raw_text[i] = "\n".join(raw_text[i])

    @classmethod
    def _join_all_pages(cls, raw_text) :

        concatenated_text = []
        for i in raw_text :
            concatenated_text.append(i)
        concatenated_text = "\n".join(concatenated_text)
        return concatenated_text

    @classmethod
    def _split_the_text_on_bold_points(cls, text) :

        split_regex = r"[0-9]+[A-Z]*\.[^\n]"
        split_text = re.split(split_regex, text)
        return split_text

    @classmethod
    def _filter_and_get_plain_text(cls, text) :

        for i in range(len(text)) :
            text[i] = re.sub(r"(“|”|’)", "\"", text[i])
            text[i] = re.sub(r"\n", " ", text[i])
            text[i] = re.sub(r" +", " ", text[i])
            text[i] = re.sub(r"—", "- ", text[i])

    @classmethod
    def _get_the_contexts(cls, text) :

        contexts = []
        for i in range(len(text)) :
            if (len(text[i].split()) <= 512) :
                contexts.append(text[i])
            else :
                temp = cls._get_contexts_greater_than_max_size(text[i])
                for i in temp :
                    contexts.append(" ".join(i))

        return contexts

    @classmethod
    def _get_contexts_greater_than_max_size(cls, text) :

        ROMAN_NUMERALS = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', \
                          'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx', \
                          'xxi', 'xxii', 'xxiii', 'xxiv', 'xxv', 'xxvi', 'xxvii', 'xxviii', 'xxix', 'xxx']
        level_wise_regex = [r"\([0-9]+\)", r"\([a-z]\)", r"\((" + "|".join(ROMAN_NUMERALS) + r")\)" , r"\([A-Z]\)"]
        punctuations = ",-.:;"
        end_markers = "."
        current_index = 0
        regex_match_flag = 0
        max_context_length = 0

        contexts = []
        text = text.split()

        while (current_index < len(text)) :

            regex_match_flag = 0
            max_context_length = min(current_index + 512, len(text))
            context = text[current_index:max_context_length]
            if max_context_length == len(text) :
                contexts.append(context)
                current_index += len(context)
            else :
                i = len(context) - 1
                while i > (len(context) // 2) :
                    # if (re.match(level_wise_regex[0], context[i]) is not None) :
                    #     print("First Matched")
                    # if (re.match(level_wise_regex[1], context[i]) is not None) :
                    #     print("Second Matched")
                    # if (re.match(level_wise_regex[2], context[i]) is not None) :
                    #     print("Third Matched")
                    # if (re.match(level_wise_regex[3], context[i]) is not None) :
                    #     print("Fourth Matched")

                    if (re.match(level_wise_regex[0], context[i]) is not None) or \
                        (re.match(level_wise_regex[1], context[i]) is not None) or \
                        (re.match(level_wise_regex[2], context[i]) is not None) or \
                        (re.match(level_wise_regex[3], context[i]) is not None) :
                        if i != 0 and context[i-1][-1] in punctuations :
                            context = context[:i]
                            contexts.append(context)
                            current_index += i
                            regex_match_flag = 1
                            break
                    i -= 1

                if not regex_match_flag :
                    i = len(context) - 1
                    while (i > 0) :
                        if context[i][-1] in end_markers :
                            context = context[:i + 1]
                            contexts.append(context)
                            current_index += (i + 1)
                            break
                        i -= 1

        if len(contexts[-1]) <= 10 :
            del contexts[-1]

        return contexts
                        
if __name__=="__main__" :
    x = TextProcessingAndContextCreation.get_context_chunks("201314.pdf")
    if x :
        for i in x :
            print(i)
            print(len(i.split()))
            print('--------------------------------')
        print(len(x))


    # get_context_chunks (name of the file) return list of contexts :
        # _get_raw_text_from_pdf (name of the file) /convert the pdf file to text (\n are removed)
        # _get_the_first_page_number (list of extracted raw text)
        # _remove_header_of_first_page (list of extracted raw text)
        # _delete_footer_notes of all the pages (list of extracted raw text from the first page onwards) (check if the pattern 
        #   like '1.' doesn't have any whitespace before it till '\n')
        # _remove_captial_words of all the pages (list of text on the pages from the previous function)
        # _join_all_pages (list of text on pages from the previous function)
        # _filter_and_get_plain_text to replace symbols like \n, dash, different types of quotes, etc.
        # _split_the_text_on_bold_points [for eg: 1. or 3.] (input is previous function output) (returns list of strings with each
        #   string beginning with 'digit.')
        # _get_the_contexts 