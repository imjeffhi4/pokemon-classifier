FROM imjeffhi4/pokemonclassifier

WORKDIR /app

COPY . /app
COPY ./public /app/public

EXPOSE 8000

CMD ["uvicorn", "pokemon_classifier:app", "--host", "0.0.0.0", "--port", "8000"]