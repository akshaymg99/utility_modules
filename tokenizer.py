"""
from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
sample = "test sentence' for checking; words like can't, {key: value}/pairs"
encoding = tokenizer.encode(sample)
print(encoding)
print(tokenizer.convert_ids_to_tokens(encoding))

# using gensim
from gensim.utils import tokenize
text = "test sentence' for checking; words like can't, {key: value}/pairs"
print(list(tokenize(text)))

# using keras tokenizer
from keras.preprocessing.text import text_to_word_sequence
text = "Characters like periods, exclamation point and newline char are used to separate the sentences. But one drawback with split() method, that we can only use one separator at a time! So sentence tonenization wont be foolproof with split() method."
text_to_word_sequence(text, split= ".", filters="!.\n")
"""

import re
def preprocess_and_tokenize(text):
    text = re.sub(r"[/,\\-]", " ", text)
    cleaned_text = re.sub(r"(?<!\w)'|'(?!\w)|[^'\w\s]", "", text)
    tokens = cleaned_text.split()
    return tokens

test_eg = "test sentence' for checking; words like can't, {key: value}/pairs, attr: value, ['fei', can't]"
tokens = preprocess_and_tokenize(test_eg)
print(tokens)


# using spacy
import re
import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import compile_infix_regex, compile_prefix_regex, compile_suffix_regex


def preprocess_text(text):
    return re.sub(r'[/,\\-]', ' ', text)

def customize_tokenizer(nlp):
    prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
    suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)
    infix_re = compile_infix_regex([r'(?<!\w)[\'\’](?=\w)|[/,\\-]'])

    tokenizer = Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                          suffix_search=suffix_re.search,
                          infix_finditer=infix_re.finditer,
                          token_match=None)

    # Add a special case rule to prevent the tokenizer from splitting at an apostrophe within words
    matcher = nlp.tokenizer.token_match

    def custom_token_match(text):
        # If the text is a single apostrophe, return None to allow default behavior
        if text == "'" or text == "’":
            return None
        # Otherwise, use the existing matcher
        return matcher(text) if matcher is not None else None

    tokenizer.token_match = custom_token_match
    return tokenizer


# Create a blank English nlp object
nlp = spacy.blank('en')

# Customize tokenizer with specific rules
nlp.tokenizer = customize_tokenizer(nlp)

# Test text
text_example = "test sentence' for checking; words like can't, {key: value}/pairs, attr: value, ['fei', can't]"

# Preprocess the text and tokenize
preprocessed_text = preprocess_text(text_example)
tokens = [token.text for token in nlp(preprocessed_text) if not token.is_space and not token.is_punct]

print(tokens)




