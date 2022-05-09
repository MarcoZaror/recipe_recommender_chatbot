# -*- coding: utf-8 -*-

import json
import os
from sacremoses import MosesTokenizer
import numpy as np
import logging
from typing import Dict
import string
from utils.tokenizer import Tokenizer
from pathlib import Path

logger = logging.getLogger("recipe_recommender")


class Data:
    def __init__(self):
        self.recipes, self.word2id, self.id2word, self.recipes_emb, self.words_emb = {}, {}, {}, {}, {}

    def load_content(self, path) -> Dict:
        logger.info("Loading recipes")
        if os.path.exists(path):
            with open(path, 'r') as fp:
                self.recipes = json.load(fp)
        else:
            self.recipes = {}
        return self.recipes
    
    def write_content(self, path_rec: Path, path_rec_emb: Path, path_w_emb: Path, path_w2i: Path, path_i2w: Path):
        logger.info("Dumping recipes")
        with open(path_rec, 'w') as fp:
            json.dump(self.recipes, fp)
        with open(path_w2i, 'w') as fp:
            json.dump(self.word2id, fp)
        with open(path_i2w, 'w') as fp:
            json.dump(self.id2word, fp)
        np.save(path_rec_emb, self.recipes_emb)
        np.save(path_w_emb, self.words_emb)

    def get_only_complete_recipes(self):
        logger.info("Filtering complete recipes")
        complete, incomplete = 0, 0
        recipes_complete = {}
        ind = 1
        for i in self.recipes.keys():
            check = self.recipes[i]
            if (check['link'] != '') and (check['tit'] != '') and (check['desc'] != ''):
                complete += 1
                recipes_complete[ind] = self.recipes[i]
                ind += 1
            else:
                incomplete += 1
        logger.info('{} % of complete recipes'.format(complete/(complete+incomplete)))
        self.recipes = recipes_complete
    
    def clean_text(self):
        """ Clean text and generate id2word and word2id mappings"""
        logger.info(" Cleaning text")
        raw_text = []
        for i in range(1, len(self.recipes)):
            desc = self.recipes[i]['tit'] + self.recipes[i]['cat'] + self.recipes[i]['desc']
            desc = desc.translate(str.maketrans('', '', string.punctuation))
            raw_text = [word.strip().lower() for word in desc.split()]
            if self.recipes[i]['pais'] != 0:
                raw_text.append(self.recipes[i]['pais'])
        raw_text = ' '.join(raw_text)

        tokenizer = Tokenizer()
        raw_text_tokenized = tokenizer.tokenize(raw_text)
        self.generate_mappings(raw_text_tokenized)  # make word2id and id2word

    def generate_mappings(self, full_text: str):
        """ Generate id2word and word2id mappings"""
        logger.info("Generate mappings")
        words_unique = set(full_text.split())
        self.word2id = {word: i for i, word in enumerate(words_unique)}
        self.id2word = {w: k for k, w in self.word2id.items()}

    def get_embeddings(self, word_embeddings_path: str = "", embeddings_size: int = 100):
        """ Obtain word embeddings and use them to generate recipe embeddings"""
        logger.info("Obtaining embeddings")
        # Load embeddings
        with open(word_embeddings_path, 'r', encoding='utf-8') as fp:
            for line in fp.readlines()[1:]:
                word = line.split()[0]
                if word in self.word2id:
                    emb = np.array(line.strip('\n').split()[1:]).astype(np.float32)
                    self.words_emb[word] = emb

        # Compute recipe embeddings
        mt = MosesTokenizer(lang='sp')
        for i in range(1, (len(self.recipes)+1)):
            desc = mt.tokenize(self.recipes[i]['tit'] + ' ' + self.recipes[i]['cat'] + ' ' + str(self.recipes[i]['pais']), escape=False)
            desc = [w.lower() for w in desc]
            # Compute embedding for the sentence
            w = 0.000000001
            emb = np.zeros(embeddings_size)
            for word in desc:
                if word in self.words_emb:
                    emb += self.words_emb[word]
                    w += 1
            self.recipes_emb[i] = emb/w
