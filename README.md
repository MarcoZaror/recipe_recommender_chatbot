## Objective
This project is focused on creating a basic chatbot that retrieve information about the user and what type of food they want to cook, and recommend recipes given that information.

To chat with the bot, use the recommend_recipe.py script. However, firstly it is needed to run the web_scrapping.py script in order to gather and structure all the necessary information.

## Some details
 - query embeddings are obtained averaging all word emebddings from the query
 - recipe embeddings are obtained concatenating the text from category, title and country of the recipe and averaging word embeddings from all that text
 - The similarity between a user query and the recipes is done using cosine similarity


## Future work
 - Try different approaches to generate embeddings. Specifically, obtaining sentence embeddings directly rather than averaging word embeddings looks like the most promising approach
 - Gather recipes from other websites

