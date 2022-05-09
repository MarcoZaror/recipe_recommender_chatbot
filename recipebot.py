# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 17:44:28 2020

@author: Marco
"""
import json
import logging
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from utils.tokenizer import Tokenizer

logger = logging.getLogger("recipe_recommender")


class RecipeBot:
    def __init__(self):
        self.recipes, self.recipes_emb, self.w_emb, self.word2id, self.query = (
            {},
            {},
            {},
            {},
            {},
        )
        (
            self.query["vegan"],
            self.query["vegetarian"],
            self.query["gluten"],
            self.query["lactosa"],
        ) = (0, 0, 0, 0)
        self.tokenizer = Tokenizer()

    def init_bot(
        self, path_rec: Path, path_rec_emb: Path, path_w_emb: Path, path_w2i: Path
    ):
        logger.info("Initializing bot")
        with open(path_rec, "r") as fp:
            self.recipes = json.load(fp)
        with open(path_w2i, "r") as fp:
            self.word2id = json.load(fp)
        self.w_emb = np.load(path_w_emb, allow_pickle=True).item()
        self.recipes_emb = np.load(path_rec_emb, allow_pickle=True).item()

    def validate_vegan(self, phrase: str):
        """Validate if a customer is vegan or vegetarian"""
        logger.info("Checking if person is vegan or vegetarian")
        phrase_lower = self.tokenizer.tokenize(phrase)

        if " ".join(phrase_lower).find("vegan") > 0:
            self.query["vegan"] = 1
        elif " ".join(phrase_lower).find("vegetarian") > 0:
            self.query["vegetarian"] = 1

    def validate_guten(self, phrase: str):
        """Validate if a customer eat gluten"""
        logger.info("Checking if person eats gluten")
        if phrase.lower().find("si") >= 0:
            self.query["gluten"] = 1

    def validate_lactose(self, phrase: str):
        """Validate if a customer eat lactose"""
        logger.info("Checking if person eats lactose")
        if phrase.lower().find("si") >= 0:
            self.query["lactosa"] = 1

    def get_recipes(self, phrase: str, embedding_size: int = 100):
        """
        Obtain recipes with the following procedure:
        1. Compute embedding for phrase
        2. Filter recipes based on query (i.e. lactose free)
        3. Provide recipes based on cosine similarity over embeddings
        """
        logger.info("Obtaining recipes")
        phrase_lower = self.tokenizer.tokenize(phrase)

        # Compute embedding for the phrase
        w = 0.000000001
        emb = np.zeros(embedding_size)
        for word in phrase_lower:
            if word in self.w_emb:
                emb += self.w_emb[word]
                w += 1
        phrase_emb = emb / w
        sims = []

        # Check if person is vegan or vegetarian and get idx of recipes matching
        matchings_veg = []
        if self.query["vegan"] == 1:
            for i, receta in self.recipes.items():
                if receta["vega"] == 1:
                    matchings_veg.append(int(i))
        elif self.query["vegetarian"] == 1:
            for i, receta in self.recipes.items():
                if receta["veg"] == 1:
                    matchings_veg.append(int(i))
        else:
            matchings_veg = [i for i in range(1, len(self.recipes))]

        # Check if person doesn't eat gluten
        matchings_glu = []
        if self.query["gluten"] == 1:
            for i, receta in self.recipes.items():
                if receta["s_glu"] == 1:
                    matchings_glu.append(int(i))
        else:
            matchings_glu = [i for i in range(1, len(self.recipes))]

        # General matching algorithm
        matchings = [value for value in matchings_veg if value in matchings_glu]
        # Check similarity between phrase and all the other recipes
        for i in range(1, (len(self.recipes) + 1)):
            if i in matchings:
                sims.append(
                    cosine_similarity(
                        self.recipes_emb[i].reshape(1, -1), phrase_emb.reshape(1, -1)
                    )[0]
                )
        results = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:5]
        print("He encontrado estas recetas!")
        for i in results:
            print(str(self.recipes[str(matchings[i])]["tit"]) + "\n")
