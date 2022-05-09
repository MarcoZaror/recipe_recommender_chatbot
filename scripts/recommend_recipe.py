# -*- coding: utf-8 -*-

from recipebot import RecipeBot
import os
from pathlib import Path


def recommend_recipe():
    bot = RecipeBot()
    
    path_rec = os.getcwd() / Path("recetas.json")
    path_w2i = os.getcwd() / Path("w2i.json")
    path_rec_emb = os.getcwd() / Path("recetas_emb.npy")
    path_w_emb = os.getcwd() / Path("w_emb.npy")
    
    bot.init_bot(path_rec, path_rec_emb, path_w_emb, path_w2i)
    print('Hola, soy receta-bot!')
    print('Para comenzar, cuentame un poco de ti..')
    print('Eres vegetariana(o) o vegana(o)?')
    is_veg = input()
    bot.validate_vegan(is_veg)
    print('Perfecto! Lo tendre en consideracion')
    print('Eres alergico o alergica al gluten?')
    is_gluten_allergic = input()
    bot.validate_guten(is_gluten_allergic)
    print('Genial.. estoy listo para recomendarte recetas!')
    print('Que te gustaria cocinar hoy?')
    food_type = input()
    bot.get_recipes(food_type)


if __name__ == '__main__':
    recommend_recipe()

