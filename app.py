#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 17:45:03 2018

@author: AB-type1
"""
# import os, sys
from flask import Flask, render_template, url_for
from Name_model import keras_Model
import tensorflow as tf
from utils import normalize
import json
import numpy as np
import collections
from datetime import datetime

#############################
#####  HELPER FUNCTIONS #####
#############################
def sort_by_lastname(lst):
    temp = []
    for x in lst:
        pos = x.rfind(' ')
        first = x[:pos]
        last = x[pos+1:]
        temp.append(last + ' ' + first)
    lst = temp
    lst.sort()
    
    temp = []
    for x in lst:
        pos = x.lfind(' ')
        last = x[:pos]
        first = x[pos+1:]
        temp.append(first + ' ' + last)
        
    return temp

def is_kr_last_name(last_name):
    return last_name.lower() in kr_last_names

def is_kr_first_name(first_name):
    first = ''
    idx = set()

    for part in first_name.split():
        _part = normalize(part)
        if len(_part) > 1:
            idx.add(np.argmax(predict(_part)))
            first += _part
    if len(first) > 1:
        arg = np.argmax(predict(first))
        if arg == 0: return True
        idx.add(arg)

    return (0 in idx) and (1 not in idx)

def predict(name):
    with graph.as_default():
        prediction = model.pred(name)
    return prediction

def init():
    f = open('./data/kr_last_names.txt', 'r')
    for line in f.readlines():
        kr_last_names.add(line.rstrip('\n').lower())
    f.close()
    global model
    model.load()
    global graph
    graph = tf.get_default_graph()


app = Flask(__name__) # placeholder for current module

@app.route('/')
def home():
    currentYear = datetime.now().year
    return render_template('home.html', years = [x for x in range(1980,currentYear+1)])


@app.route('/')
@app.route('/<name>')
def display(name):
    
    fromyear = int(name[0:4])
    toyear = int(name[4:8])
    option = int(name[8])
    journals = name[9:].split('_')[1:-1]
    title1 = "from " + str(fromyear) + " to " + str(toyear)
    title2 = ", ".join(journals)
    
    # load data from database, for journals, fromyear ~ toyear
    big_dictionary = dict([])
    for journal in journals:
        for x in range(toyear, fromyear-1, -1):
            try:
                if option == 2:
                    temp = "_by_first.json"
                elif option == 3:
                    temp = "_by_last.json"
                else:
                    temp = "_by_every.json"
                with open("./dblp/"+journal+"/"+journal+str(x)+ temp,'r') as f:
                    dictionary = json.load(f)
                    temp = list(dictionary.keys())
                    for author in temp:
                        tttt = author.split()
                        _author = tttt[-1] + ', ' + ' '.join(tttt[:-1])
                        try:
                            big_dictionary[_author] += dictionary[author]
                        except KeyError:
                            big_dictionary[_author] = dictionary[author]
            except FileNotFoundError:
                pass


    # big_dictionary available
             
    
    
    korean_names = []
    non_korean_names = []
    
    # Do classification
    
    for author in big_dictionary.keys():
        temp = author.rfind(" ")
        last = author[temp+1:].lower()
        first_raw = author[:temp].lower()

        if is_kr_last_name(last) and is_kr_first_name(first_raw):
            korean_names.append(author)
        else:
            non_korean_names.append(author)
        # first = ''
        # for part in first_raw.split():
        #     first += normalize(part)
        #
        # if last in kr_last_names:
        #     with graph.as_default():
        #         prediction = model.pred(first)
        #     if np.argmax(prediction) == 0:
        #         korean_names.append(author)
        #     else:
        #         non_korean_names.append(author)
        # else:
        #     non_korean_names.append(author)
            
    korean_names.sort()
    non_korean_names.sort()
    
    # korean_names = korean_names[:100]
    # non_korean_names = non_korean_names[:100]
    
    
    
    # Display options:
    # 0. Default: Alphabetical
    # 1. Number of papers
    # 2. View first authors only
    # 3. View last authors only
    
    # Data ready: 1. (non_)korean_names (list), 2. big_dictionary

    if option == 0:
        pass
        
    elif option == 1:
        kr = [(-len(big_dictionary[x]), x) for x in korean_names]
        kr.sort()
        korean_names = []
        for i in range(len(kr)):
            korean_names.append(kr[i][1])
        
        nonkr = [(-len(big_dictionary[x]), x) for x in non_korean_names]
        nonkr.sort()
        non_korean_names = []
        for i in range(len(nonkr)):
            non_korean_names.append(nonkr[i][1])

    return render_template('display.html',
                           name = str(name).upper(), 
                           dictionary = big_dictionary,
                           korean_names = korean_names,
                           non_korean_names = non_korean_names,
                           title1 = title1, title2 = title2)

if __name__ == '__main__':
    kr_last_names = set()
    model = keras_Model()
    graph = None
    init()
    app.run(debug = True, port = 5003)