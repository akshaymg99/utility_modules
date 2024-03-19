import re
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from nltk.corpus import stopwords
en_stop = stopwords.words('english')
import spacy
nlp = spacy.load("en_core_web_md")


class NormalizeString:
    def __init__(self):
        self.noise_word_len = 2

    def truncate(self, no, place_digits):
        """
        Truncates a float no place_digits decimal places without rounding
        """
        float_str = '%.{}f'.format(place_digits)
        return float(float_str % no)

    def remove_noise(self, text):
        if str(text) == 'nan' or str(text) == 'None':
            return ''

        word_lst = []
        for word in text.split(): 	 ## removes extra whitespace inbetween words also
            if word in en_stop or len(word) > self.noise_word_len:
                word_lst.append(word)
        return ' '.join(word_lst)

    def remove_dup(self, string):
        word_lst = string.split()
        new_word_lst = []
        i_w = 0
        while (i_w < len(word_lst) - 1):
            new_word_lst.append(word_lst[i_w])
            if str(word_lst[i_w]) == str(word_lst[i_w + 1]):
                i_w += 1
            i_w += 1

        if len(word_lst) >= 2 and str(word_lst[-1]) != str(word_lst[-2]):
            new_word_lst.append(word_lst[-1])
        return " ".join(new_word_lst)

    def remove_stopwords(self, row):
        row = row.split()
        filtered_words = [word for word in row if word not in en_stop]
        return " ".join(filtered_words)

    def lemmatize_sentence(self, sentence):
        doc = nlp(sentence)
        empty_list = []
        for token in doc:
            empty_list.append(token.lemma_)
        final_string = ' '.join(map(str, empty_list))
        return final_string

    def preprocess_string(self, row):
        row = str(row)
        if row == '' or row == 'nan' or row == 'None':
            return ''
        row = str(row)
        row = row.lower().strip()
        # punctuation = "!@#$%^&*()[]{};:.<>?\|`~-=_+"
        punctuation = '''''!()[]{};:'"\.?@#$%^&*_~'''
        row = row.replace(',', ' ').replace('-', ' ').replace('/', ' ')
        # remove punctuation from the string
        no_punct = ""
        for char in row:
            if char not in punctuation:
                no_punct = no_punct + char
        row = no_punct

        l = []
        for token in row.split():
            if token not in en_stop:
                #l.append(stemmer.stem(token))
                l.append(lemmatizer.lemmatize(token))
        row = " ".join(l)

        row = re.sub(r'[0-9]+', '', row)
        row = self.remove_noise(row)
        row = self.remove_dup(row)
        # Comment out these modules for lang model use
        row = self.remove_stopwords(row)
        row = self.lemmatize_sentence(row)

        return row.strip()
