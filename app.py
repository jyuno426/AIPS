#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 17:45:03 2018
@author: Seunghyun Lee, Junho Han
"""
from flask import Flask, render_template
from datetime import datetime
import json, os, copy

#############################
#####  HELPER FUNCTIONS #####
#############################
def dict_update(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1:
            dict1[key] += value
        else:
            dict1[key] = value


data = {}
min_year = 1960
max_year = datetime.now().year
area_table = json.load(open('./database/area_table.json'))

app = Flask(__name__)  # placeholder for current module


@app.route('/')
def home():
    return render_template('home.html', years=range(min_year, max_year + 1), area_table=area_table)


@app.route('/<name>')
def display(name):
    fromyear = int(name[0:4])
    toyear = int(name[4:8])
    option = int(name[8])
    show_howmany = [10, 25, 50, 100, 200][int(name[9])]
    conf_list = sorted(name[10:].replace('-', ' ').lower().split('_')[1:-1])
    filters = ['every', 'every', 'first', 'last']

    # Display options:
    # 0. all
    # 1. only korean
    # 2. only first author
    # 3. only last author

    big_dict = {}
    names = set()

    # load data from database, for each conf, fromyear ~ toyear
    for conf in conf_list:
        for year in range(toyear, fromyear-1, -1):
            kr_dict = copy.deepcopy(data[conf][year][filters[option]][0])
            names.update(list(kr_dict.keys()))
            dict_update(big_dict, kr_dict)

            if option != 1:
                nonkr_dict = copy.deepcopy(data[conf][year][filters[option]][1])
                names.update(list(nonkr_dict.keys()))
                dict_update(big_dict, nonkr_dict)

    # Choose top "show_howmany" authors in terms of # of papers
    # Sort those authors by lexicographic order (last name, first name)

    temp1 = sorted([(-len(big_dict[x]), x) for x in names])[:show_howmany]
    temp2 = sorted([(x[1].split()[-1], x[1]) for x in temp1])
    name_list = [x[1] for x in temp2]

    # For display, e.g. Jinwoo Shin
    # NIPS=3, ICML=3, AISTATS=4 (TOTAL=10)

    part_dict = {}
    info_dict = {}
    for author in name_list:
        info_dict[author] = {}
        part_dict[author] = (big_dict[author], len(big_dict[author]))
        for paper in big_dict[author]:
            try:
                info_dict[author][paper[3].upper()] += 1
            except KeyError:
                info_dict[author][paper[3].upper()] = 1

    for author in name_list:
        temp = ""
        for conf in sorted(info_dict[author].keys()):
            temp += conf + "=" + str(info_dict[author][conf]) + ', '
        info_dict[author] = temp[:-2]

    return render_template('display.html',
                           name=name,
                           dictionary=part_dict,
                           name_list=name_list,
                           info_dict=info_dict,
                           kroption=option - 1)


def init():
    from utils import get_file
    for conf in get_file('./data/conferences.txt'):
        data[conf] = {}
        print('Initial Load: ' + conf.upper())
        for year in range(min_year, max_year + 1):
            data[conf][year] = {}
            for how in ['every', 'first', 'last']:
                path = './database/' + conf.upper() + '/' +\
                       conf.lower() + str(year) + '_' + how + '_'
                if os.path.exists(path + 'kr.json'):
                    data[conf][year][how] = [
                        json.load(open(path + 'kr.json')),
                        json.load(open(path + 'nonkr.json'))
                    ]
                else:
                    data[conf][year][how] = [{}, {}]


if __name__ == '__main__':
    init()
    app.run(port=5002)
