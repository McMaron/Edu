    #!/usr/bin/env python3

import os
import sys
import nltk

from nltk.tokenize import TweetTokenizer
from analyzer import Analyzer
from termcolor import colored
from helpers import get_user_timeline

tweet_list = get_user_timeline("@lis_tomasz", 10)

tknzr = TweetTokenizer()
ciag =  "O co ci chodzi, glabie?"
tokens = tknzr.tokenize(ciag)
print(tokens)
print(ciag)
