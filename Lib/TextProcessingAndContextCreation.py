import pdftotext 
import re

class TextProcessingAndContextCreation :

    @classmethod
    def get_context_chunks(cls, file_name) :
        
        # Get the list of strings where each string is the text content present
        # each page of the pdf document
        raw_text = cls._get_raw_text_from_pdf(file_name)

        # Remove the index part of the doc; for this, page number of the first
        # main content page is required
        first_page_number = cls._get_the_first_page_number(raw_text)
        if first_page_number == -1 :
            print("Error encountered")
            return []

        # Get only the content pages
        raw_text = raw_text[first_page_number:]

        # The first content page has the title of the Act. Remove it
        cls._remove_header_of_first_page(raw_text)

        # Delete the footer notes, that are generally the references from other
        # acts or some points giving additional info about those acts
        cls._delete_footer_notes(raw_text)

        # Words like "CHAPTER" are of no use for context. Remove them
        cls._remove_captial_words(raw_text)

        # Join the content of all the pages to get a single string
        text = cls._join_all_pages(raw_text)

        # Split the text into context chunks at the bold points present in the Act.
        text = cls._split_the_text_on_bold_points(text)

        # Remove unwanted newline, spaces, unrecognized quotes, and other symbols.
        cls._filter_and_get_plain_text(text)

        # For every chunk we extracted before, if the size of the chunk goes beyond
        # the limit, split that chunk as well with some defined procedure. Check
        # the function for more details
        contexts =  cls._get_the_contexts(text)
        # return the contexts
        return contexts

    @classmethod
    def _get_raw_text_from_pdf(cls, file_name) :

        # Open the file and read the text
        with open(file_name, "rb") as f :
            pdf_text = pdftotext.PDF(f)
        
        # Append the text present on each page to the list and return it
        raw_text = []
        for i in pdf_text :
            raw_text.append(str(i))
        return raw_text

    @classmethod
    def _get_the_first_page_number(cls, raw_text) :

        # Use the string 'ACT,' present in the title of the Act to mark the title
        # present in the content pages and remove it.
        # If the word 'ACT,' is not found, use the year (DDDD) to mark the title
        index = -1
        try :
            # Get the index of the string 'ACT,' present in the title of the first
            # index page
            index = raw_text[0].split().index('ACT,')
        except :
            # If 'ACT,' is not found, use year
            year_regex = r"[0-9]{4}"
            for i in range(len(raw_text[0].split())) :
                if (re.match(year_regex, raw_text[0].split()[i])) is not None :
                    index = i
                    break

        # If both 'ACT,' and year is not found, report error
        if index == -1 :
            return -1

        # Get the title of the Act using the index calculated.
        # A typical title is like 'EDUCATION ACT, 2002'
        match_text_page_zero = " ".join(raw_text[0].split()[:index + 1])
        # Match the title with the later pages and when it is found, that one is
        # the first content page.
        for i in range(1, len(raw_text)) :
            page_match_text = " ".join(raw_text[i].split()[:index + 1])
            if match_text_page_zero == page_match_text :
                return i

        # Failed
        return -1

    @classmethod
    def _remove_header_of_first_page(cls, raw_text) :

        # Remove the header present on the first content page.
        # The title/header ends with a date enclosed in square brackets
        # Use regex to match it and perform its deletion
        temp = re.match(r"(.|\n)*?\[.*\]", raw_text[0])
        raw_text[0] = raw_text[0][temp.end():]

    @classmethod
    def _delete_footer_notes(cls, raw_text) :

        # Remove the footer of the form "1. ...\n2. ..."
        footer_regex = r"1\..*"
        # For every page
        for i in range(len(raw_text)) :
            # Split on newline
            temp = raw_text[i].split('\n')[:-2]
            # Match the mentioned regex; j is the starting index of the footer
            for j in range(len(temp) - 1, -1, -1) :
                if re.match(footer_regex, temp[j]) is not None :
                    break
            # Discard the footer
            if j != 0 :
                temp = temp[:j]
            # Rejoin using the newline character
            raw_text[i] = "\n".join(temp)

    @classmethod
    def _remove_captial_words(cls, raw_text) :

        # Split each page using \n (newline) to get each line.
        # If the string is uppercase, remove it
        # Rejoin the text
        for i in range(len(raw_text)) :
            raw_text[i] = raw_text[i].split('\n')
            raw_text[i] = list(filter(lambda x: not (x.isupper()), raw_text[i]))
            raw_text[i] = "\n".join(raw_text[i])

    @classmethod
    def _join_all_pages(cls, raw_text) :

        # Join all the pages into one long string
        concatenated_text = []
        for i in raw_text :
            concatenated_text.append(i)
        concatenated_text = "\n".join(concatenated_text)
        return concatenated_text

    @classmethod
    def _split_the_text_on_bold_points(cls, text) :

        # The starting of each point has the form "1. <text> ...
        # Use it for splitting the continuous text into pointwise text
        split_regex = r"[0-9]+[A-Z]*\.[^\n]"
        split_text = re.split(split_regex, text)
        return split_text

    @classmethod
    def _filter_and_get_plain_text(cls, text) :

        # Get rid off unwanted symbols
        for i in range(len(text)) :
            text[i] = re.sub(r"(“|”|’)", "\"", text[i])
            text[i] = re.sub(r"\n", " ", text[i])
            text[i] = re.sub(r" +", " ", text[i])
            text[i] = re.sub(r"––", "- ", text[i])
            text[i] = re.sub(r"—", "- ", text[i])

    @classmethod
    def _get_the_contexts(cls, text) :

        # For each bold point in the list
        contexts = []
        for i in range(len(text)) :
            # If the section is less than 20 words, it is not a good candidate
            if (len(text[i].split()) < 20) :
                continue
            # If the section is greater than 20 words and less than 350 words,
            # it is a good candidate
            elif (len(text[i].split()) >= 20 and len(text[i].split()) <= 350) :
                contexts.append(text[i])
            # If the section is greater than 350 words, break that section further
            # using some rules
            else :
                temp = cls._get_contexts_greater_than_max_size(text[i])
                for i in temp :
                    contexts.append(" ".join(i))

        # return contexts
        return contexts

    @classmethod
    def _get_contexts_greater_than_max_size(cls, text) :

        ROMAN_NUMERALS = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', \
                          'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx', \
                          'xxi', 'xxii', 'xxiii', 'xxiv', 'xxv', 'xxvi', 'xxvii', 'xxviii', 'xxix', 'xxx' \
                          'xxxi', 'xxxii', 'xxxiii', 'xxxiv', 'xxxv', 'xxxvi', 'xxxvii', 'xxxviii', 'xxxix', 'xl' \
                          'xli', 'xlii', 'xliii', 'xliv', 'xlv', 'xlvi', 'xlvii', 'xlviii', 'xlix', 'l', \
                          'li', 'lii', 'liii', 'liv', 'lv', 'lvi', 'lvii', 'lviii', 'lix', 'lx']

        # Regex for points. The points are often nested. The hierarchy of the points
        # is like this : Points starting with (1), (2) are the top ones, then (a), (b)
        # comes below it, then (i), (ii) and then (A) (B).
        level_wise_regex = [r"\([0-9]+\)", r"\([a-z]{1,2}\)", r"\((" + "|".join(ROMAN_NUMERALS) + r")\)" , r"\([A-Z]\)"]
        punctuations = ",-.:;"
        end_markers = ".;"
        current_index = 0
        regex_match_flag = 0
        max_context_length = 0

        contexts = []
        text = text.split()

        # Traverse through the text
        while (current_index < len(text)) :

            regex_match_flag = 0
            # Find the end index of the chunk considering the limits
            max_context_length = min(current_index + 350, len(text))
            context = text[current_index:max_context_length]
            # Check if this is the last chunk
            if max_context_length == len(text) :
                contexts.append(context)
                current_index += len(context)
            # If it is not the last chunk.
            else :
                # Find the possible end of that chunk by backtraversing. Find
                # the start of the current point by matching the regex and add
                # the context upto that index.
                # Backtrack half the length of current context.
                i = len(context) - 1
                while i > (len(context) // 2) :

                    # Try matching one of the regular expression
                    if (re.match(level_wise_regex[0], context[i]) is not None) or \
                        (re.match(level_wise_regex[1], context[i]) is not None) or \
                        (re.match(level_wise_regex[2], context[i]) is not None) or \
                        (re.match(level_wise_regex[3], context[i]) is not None) :
                        # The previous word should end with punctuation
                        if i != 0 and context[i-1][-1] in punctuations :
                            # Record the context, move the current index and the
                            # set the regex match flag to skip the next checking
                            context = context[:i]
                            contexts.append(context)
                            current_index += i
                            regex_match_flag = 1
                            break
                    i -= 1

                # If no regex is matched, backtrack and check for endmarker punctuation
                # like full-stop.
                if not regex_match_flag :
                    i = len(context) - 1
                    while (i > 0) :
                        if context[i][-1] in end_markers :
                            context = context[:i + 1]
                            contexts.append(context)
                            current_index += (i + 1)
                            break
                        i -= 1

            # Context less than 20 words are discarded.
            if len(contexts[-1]) < 20 :
                del contexts[-1]

        # Return the contexts
        return contexts
                        
if __name__=="__main__" :
    x = TextProcessingAndContextCreation.get_context_chunks("The Code on Wages, 2019.pdf")
    # x = TextProcessingAndContextCreation.get_context_chunks("Anti-Hijacking Act, 2016.pdf")
    # x = TextProcessingAndContextCreation.get_context_chunks("Sexual Harassment Act, 2013.pdf")
    # x = TextProcessingAndContextCreation.get_context_chunks("Advocates' Welfare Fund Act, 2001.pdf")
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
