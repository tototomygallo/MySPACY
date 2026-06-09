import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Across the bridge and beneath the old station, the researcher walked through the crowded market with a notebook in her hand and a camera around her neck, while several tourists from nearby towns argued about the paintings on the walls and the music coming from the cafés behind them. During the afternoon, she sat beside a fountain in front of the museum and wrote comments about the conversations between the vendors and the visitors, even though a sudden storm moved over the city and into the narrow streets around the square. Later, according to the guide standing near the entrance, a group of students ran out of the library, across the park, and toward the river after the lights inside the building went off.")

for token in doc:
    print(token.text, token.pos_, token.tag_, token.dep_)