from collections import Counter
from decimal import *
import math
import os
import pprint

from flask import Flask, \
                  abort, \
                  jsonify, \
                  render_template, \
                  request, \
                  redirect, \
                  send_from_directory
import requests
from bs4 import UnicodeDammit, BeautifulSoup

from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer

from pattern.en import lemma as lemmatizer_en
from pattern.nl import lemma as lemmatizer_nl

import numpy

import obo
from text_parser import TextProcessor

app = Flask(__name__)

text_processor = TextProcessor()    

re_vowel_en = re.compile("[aAeEiIoOuU]")
re_vowel_nl = re.compile("IJ|ij|[aAeEiIoOuU]")

@app.route('/app/<path:path>')
def send_file(path):
    return send_from_directory('user_interface/app', path) 

@app.route('/', methods=['GET','POST'])
def hello_world():
    if request.method == "GET":
        return redirect("/app/index.html")
    else:
        pprint.pprint(request.form)
        pprint.pprint(request.files)
        
        #Language check
        if request.form['language'] not in ['english', 'dutch']:
            return jsonify(status='error', message="Invalid language!")
        
        #Input normalization
        if request.form['upload_option'] == 'text_field':
            input_text = request.form['upload_textarea']
        elif request.form['upload_option'] == 'url':
            page_text = requests.get(request.form['upload_url']).text
            soup = BeautifulSoup(page_text, "html.parser")
            input_text = soup.text
        elif request.form['upload_option'] == 'file':
            input_text = UnicodeDammit(request.files.get('upload_file').read()).unicode_markup
            
        #Stemmer selection
        if request.form['stemmer'] == 'no_stemmer':
            stemmer = None
        elif request.form['stemmer'] == 'porter':
            if request.form['language'] != 'english':
                return jsonify(status='error', message="Invalid language for stemmer porter!")
            stemmer = PorterStemmer()
        elif request.form['stemmer'] == 'snowball':
            stemmer = SnowballStemmer(request.form['language'])
        else:
            return jsonify(status='error', message="Invalid stemmer!")
                
        #Lemmatizer selection
        if request.form['lemmatizer'] == 'lemmatizer_off':
            lemmatizer = None
        elif request.form['language'] == 'english':
            lemmatizer = lemmatizer_en
        else:
            lemmatizer = lemmatizer_nl
            
        #Stopwords selection    
        if request.form['stopwords'] == 'no_stopwords':    
            stopwords = None
        elif request.form['stopwords'] == 'our_stopwords':
            stopwords = obo.stopwords
        elif request.form['stopwords'] == 'custom_stopwords':
            custom_stopword_text = UnicodeDammit(request.files.get('custom_stopword_file').read()).unicode_markup
            stopwords = obo.stripNonAlphaNum(custom_stopword_text)
            
        #Process the text  
        input_text_word_count = 0
        resulting_text = ""
        final_wordlist = []
        for word_type, word in text_processor.parse_text(input_text):
            if word_type == "non-word":
                resulting_text += word
            else:
                input_text_word_count += 1
                processed_word = word
                if stemmer:
                    processed_word = stemmer.stem(processed_word)
                if lemmatizer:
                    processed_word = lemmatizer(processed_word)
                if not stopwords or processed_word not in stopwords:
                    if request.form['exclude_vowels'] == 'exclude_vowels_yes':
                        if request.form['language'] == 'english':
                            regex = re_vowel_en
                        else:
                            regex = re_vowel_nl
                        processed_word = regex.sub("", processed_word)
                    resulting_text += processed_word
                    final_wordlist.append(processed_word)
          
        dictionary = obo.wordListToFreqDict(final_wordlist)
        sorteddict = obo.sortFreqDict(dictionary)   
          
        ignore_results_amount = int(request.form['ignore_results_amount'])  
          
        if ignore_results_amount > 0:
            initial_index = ignore_results_amount
            ignored_words = [word for rank, word in sorteddict[:initial_index]]
            sorteddict = sorteddict[initial_index:]    
            new_text = ""
            new_wordlist = []
            for word_type, word in text_processor.parse_text(resulting_text):
                if word_type == "non-word":
                    new_text += word
                elif word not in ignored_words:
                    new_text += word
                    new_wordlist.append(word)
            resulting_text = new_text
            final_wordlist = new_wordlist
                    
        else:
            initial_index = 0          
          
        #Do the math!    
        input_text_char_count = len(input_text)
        word_count = len(final_wordlist)    
        distinct_words_count = len(sorteddict)
        words = []
        frequencies = []
        word_cloud = []
        for frequency, word in sorteddict:
            words.append(word)
            frequencies.append(frequency)
            word_cloud.append([word, frequency])

        acum_perc = Decimal(0)
        percentages = []
        acum_perc_list = []
        for freq in frequencies:
            perc = Decimal((freq*100.0)/word_count)
            percentages.append(round(perc, 2))
            acum_perc += perc
            acum_perc_list.append(round(acum_perc, 2))
            
            
        logarithms = []    
        for i in range(len(sorteddict)):    
            logarithms.append((math.log(i+1), math.log(frequencies[i])))
            
        #Calculate Linear regression
        #http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.lstsq.html#numpy.linalg.lstsq
        x = numpy.array([math.log(f) for f in frequencies])
        y = numpy.array([math.log(rank) for rank in range(1, distinct_words_count + 1)])
        A = numpy.vstack([x, numpy.ones(len(x))]).T
        m, c = numpy.linalg.lstsq(A, y)[0]
        
        #Calculate the regression line start and end, 
        #  and sort making the start be the one with the lower X value
        #  (highcharts requires this)
        regline_start = (0, c)
        regline_end = (math.log(distinct_words_count), math.log(distinct_words_count) * m + c)
        regression_line = {
            'start': regline_start,
            'end': regline_end
        }
            
        return jsonify(status='success', 
                       words=words,
                       frequencies=frequencies,
                       percentages=percentages,
                       acum_perc_list=acum_perc_list,
                       logarithms=logarithms,
                       regression_line=regression_line,
                       resulting_text=resulting_text,
                       input_text_char_count=input_text_char_count,
                       input_text_word_count=input_text_word_count,
                       output_text_word_count=word_count,
                       word_cloud=word_cloud,
                       sorteddict=sorteddict)

if __name__ == '__main__':
    app.run(debug=True)




