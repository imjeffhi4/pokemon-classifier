[![Run on Ainize](https://ainize.ai/images/run_on_ainize_button.svg)](https://ainize.web.app/redirect?git_repo=https://github.com/imjeffhi4/pokemon-classifier)

# Pokémon Classifier

![Demo of the model deployed on the Ainize Platform.](https://i.ibb.co/3srB9zt/demo-alternate.gif)

Demo of the model deployed on the Ainize Platform.

# Intro

This repository contains the docker file used to build the Svelte app shown in the GIF above. It uses a fine-tuned version of ViT trained on a dataset of Pokemon I collected. If you’re interested in using this model, I’ve also made it available on Hugging Face [here](https://huggingface.co/imjeffhi/pokemon_classifier). 

# About

- Data was collected using a mixture of [Veekun images](https://veekun.com/dex/downloads), [PokemonDB](https://pokemondb.net/), and images scraped from [Brave Search](https://brave.com/search/).
- Training was performed using PyTorch-lightning and used ViT-base (see training folder for source code).
- Frontend demo was created using Svelte which was served using FastAPI.

If you'd like more information about this model, check out my [Medium post](https://medium.com/@imjeffhi4/tutorial-using-vision-transformer-vit-to-create-a-pok%C3%A9mon-classifier-cb3f26ff2c20).

# Results

The model was able to achieve 95% accuracy on my validation dataset. Though, feel free to check out the demo and try it yourself!
