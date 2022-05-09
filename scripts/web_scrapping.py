# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 20:19:27 2020

@author: Marco
"""

from data import Data
from Scrapping import WebScrapper
import os
import requests
from utils.seeds import WEBPAGE_SEEDS
from pathlib import Path


def web_scrapping():
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

    ct = Data()
    recipes = {}
    key = len(recipes) + 1
       
    sc = WebScrapper(headers, WEBPAGE_SEEDS)
    links = sc.look_for_links()
    for link in links:
        try:
            recipes = sc.grab_content(link[0], recipes, key, link[1])
            key += 1
        except requests.ConnectionError:
            continue
    ct.recipes = recipes
    ct.get_only_complete_recipes()
    ct.clean_text()
    ct.get_embeddings()
    
    path_rec = os.getcwd() / Path("recetas.json")
    path_w2i = os.getcwd() / Path("w2i.json")
    path_i2w = os.getcwd() / Path("i2w.json")
    path_rec_emb = os.getcwd() / Path("recetas_emb.npy")
    path_w_emb = os.getcwd() / Path("w_emb.npy")
    
    ct.write_content(path_rec, path_w2i, path_i2w, path_rec_emb, path_w_emb)


if __name__ == '__main__':
    web_scrapping()