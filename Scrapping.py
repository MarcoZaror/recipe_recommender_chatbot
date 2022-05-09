# -*- coding: utf-8 -*-

import logging

import requests
from bs4 import BeautifulSoup

from utils.countries import COUNTRIES

logger = logging.getLogger("recipe_recommender")


class WebScrapper:
    def __init__(self, headers, seeds):
        self.headers = headers
        self.seeds = seeds

    def look_for_links(self, max_links_per_seed: int = 20):
        logger.info("Getting links")
        link_total = []
        for seed in self.seeds:
            init = seed.find("-de-")
            end = seed.find("-listado")
            category = seed[init + 4 : end]
            for i in range(1, max_links_per_seed):
                seed = seed[:-6] + str(i) + seed[-5:]
                request = requests.get(seed)
                if request.status_code != 200:
                    continue
                r = requests.get(seed, headers=self.headers)
                a = r.text
                soup = BeautifulSoup(a, "lxml")
                links = [a.get("href") for a in soup.find_all("a", href=True)]
                for link in links:
                    link_total.append((link, category))
        # Clean links (get only the ones with recipes)
        match = "https://www.recetasgratis.net/receta-"
        links_recipes = []
        for l in link_total:
            if l[0][:37] == match:
                links_recipes.append(l)

        links_recipes = list(set(links_recipes))
        return links_recipes

    def grab_content(self, link, recetas, ind, category):
        """Store all content from webpage"""
        logger.info("Storing content from link")
        r = requests.get(link, headers=self.headers)
        text = r.text
        soup = BeautifulSoup(text, "lxml")

        # get title
        title = soup.find("h1", {"class": "titulo titulo--articulo"})
        title_clean = title.text.strip()
        recetas[ind]["title"] = title_clean

        # Get text
        description = soup.find("div", {"class": "intro"})
        description_clean = description.text.strip()
        recetas[ind]["desc"] = description_clean

        # Get people
        people = soup.find("span", {"class": "property comensales"})
        people_clean = people.text.strip()
        recetas[ind]["com"] = people_clean

        # Get duration
        duration = soup.find("span", {"class": "property duracion"})
        duration_clean = duration.text.strip()
        recetas[ind]["dur"] = duration_clean

        # Get difficulty
        difficulty = soup.find("span", {"class": "property dificultad"})
        difficulty_clean = difficulty.text.strip()
        recetas[ind]["dif"] = difficulty_clean

        # Additional features
        extras = soup.find("div", {"class": "properties inline"})
        extras_clean = extras.text.strip()
        recetas[ind]["prop"] = extras_clean

        recetas[ind]["veg"] = 1 if extras_clean.find("vegetarianos") > 1 else 0
        recetas[ind]["vega"] = 1 if extras_clean.find("veganos") > 1 else 0
        recetas[ind]["s_az"] = 1 if extras_clean.find("sin azúcar") > 1 else 0
        recetas[ind]["s_glu"] = 1 if extras_clean.find("sin gluten") > 1 else 0
        recetas[ind]["s_la"] = 1 if extras_clean.find("sin lactosa") > 1 else 0
        recetas[ind]["s_sal"] = 1 if extras_clean.find("sin sal") > 1 else 0

        if extras_clean.find("Nada picante") > 1:
            recetas[ind]["pic"] = 1
        elif extras_clean.find("Poco picante") > 1:
            recetas[ind]["pic"] = 2
        elif extras_clean.find("Picante") > 1:
            recetas[ind]["pic"] = 3
        elif extras_clean.find("Muy picante") > 1:
            recetas[ind]["pic"] = 4
        else:
            recetas[ind]["pic"] = 0

        p = 0
        for country in COUNTRIES:
            if extras_clean.find(country[0]) > 1:
                recetas[ind]["pais"] = country[1]

        # Get ingredients
        ing = []
        i = 1
        ingredients = soup.findAll("label", {"for": "ingrediente-{}".format(1)})
        for o in ingredients:
            ing.append(o.text.strip())
        while len(ingredients) > 0:
            i += 1
            ingredients = soup.findAll("label", {"for": "ingrediente-{}".format(i)})
            for o in ingredients:
                ing.append(o.text.strip())

        recetas[ind] = {}
        recetas[ind]["cat"] = category
        recetas[ind]["link"] = link
        recetas[ind]["ing"] = ing

        return recetas
