#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 16:03:41 2020

@author: juanporras
"""

import pandas as pd
import numpy as np

import json
import urllib.request
from urllib.request import urlopen

import datetime
import time

config = {'displayModeBar': False}

from cleaning_datas import df

OWData = pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv")

