import re
from itertools import groupby

# For markdown stripping
from markdown import markdown
from BeautifulSoup import BeautifulSoup

import enchant
from unidecode import unidecode
import spacy

# Tokenizer
_spacy_tokenizer = spacy.load('en')
tokenizer_name = "spacy"

# Regular expressions used to tokenize
_WORD_SPLIT = re.compile(b"([.,!?\"':;)(])")
_DIGIT_RE = re.compile(br"\d")
_URL_RE = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>\"\']+))')

# Dictionary for english
_EN_DICT = enchant.Dict("en_US")


def basic_tokenizer(sentence):
    """Very basic tokenizer: split the sentence into a list of tokens."""
    words = []
    for space_separated_fragment in sentence.strip().split():
        words.extend(re.split(_WORD_SPLIT, space_separated_fragment))
    return [w.lower() for w in words if w]


def reddit_tokenizer(raw_sentence):
    """Tokenizer for reddit comments; split the sentence into a list of tokens."""
    sentence = raw_sentence.lower()

    # Remove markdown formatting
    sentence = strip_markdown(sentence)

    # Delete word between "["~"]" and "("~")"
    sentence = re.sub(r"\[[^\]]+\]", "", sentence)
    sentence = re.sub(r"\([^\)]+\)", "", sentence)

    # Remove urls
    sentence = _URL_RE.sub("", sentence)

    # Incoporate /r/subredditname to subredditspecialtoken
    sentence = re.sub(r"/r/([^\s/]+)", "subredditspecialtoken", sentence)
    sentence = re.sub("subredditspecialtoken/", "subredditspecialtoken", sentence)

    # Incoporate /u/username to usernamespecialtoken
    sentence = re.sub(r"/u/([^\s/]+)", "usernamespecialtoken", sentence)
    sentence = re.sub("usernamespecialtoken/", "usernamespecialtoken", sentence)

    # Delete \n
    sentence = re.sub(r"\n+", " ", sentence)

    # Delete -
    sentence = re.sub(r"-", " ", sentence)
    # Incorporate ; to .
    sentence = re.sub(r";", r".", sentence)

    # Remove duplicates on . , ! ?
    sentence = re.sub(r"([!?,\.\"])\1+", r"\1", sentence)

    # Put space betwen char[.,?!][char|\n| ]
    sentence = re.sub(r"([a-zA-Z])([.,?!])([a-zA-Z\n ])", r"\1 \2 \3", sentence)

    # Normalize digits
    sentence = re.sub(br"\d+", "0", sentence)
    sentence = re.sub(r"0.0", "0", sentence)

    # Run unidecode
    sentence = unidecode(sentence)

    if tokenizer_name == "spacy":
        if type(sentence) == str:
            sentence = sentence.decode('unicode-escape')
        spacy_sentence = _spacy_tokenizer(sentence)
        sentence = [t.text for t in spacy_sentence]
        sentence = ' '.join(sentence)
        sentence = sentence.split()
        # Remove consecutive duplicate
        sentence = [x[0] for x in groupby(sentence)]
    else:
        raise NotImplementedError()

    return sentence


def strip_markdown(markdown_text):
    html = markdown(markdown_text)
    pure_text = ''.join(BeautifulSoup(html).findAll(text=True))
    return pure_text
