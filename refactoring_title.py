import re
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_md")

def is_irrelevant_keyword(text):
     if re.match(r"(\b[A-Za-z0-9]{1,3}\b)", text):
          return True
     return False

def simplify_title(title):
     simplified_keywords = []

     # Split the title into parts
     title_parts = re.split(r"[/|:;]+", title)

     for part in title_parts:
          doc = nlp(part)

          # Extract important entities
          for ent in doc.ents:
               if ent.label_ in ["PRODUCT", "ORG"]:
                    simplified_keywords.append(ent.text)

          # Extract important nouns, adjectives and verbs
          for token in doc:
               if token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"]:
                    if token.dep_ not in ["compound"] or token.head.pos_ in ["NOUN", "PROPN"]:
                         simplified_keywords.append(token.text)

     # Filter out irrelevant keywords
     simplified_keywords = [kw for kw in simplified_keywords if not is_irrelevant_keyword(kw)]
     
     # Remove duplicates and join keywords
     simplified_title = " ".join(sorted(set(simplified_keywords), key=simplified_keywords.index))
     return simplified_title



def find_product_type(title):
    product_keywords = []

    # Split the title into parts
    title_parts = re.split(r"[/|:;]+", title)

    for part in title_parts:
        doc = nlp(part)

        # Extract important entities
        for ent in doc.ents:
            if ent.label_ in ["PRODUCT", "ORG"]:
                product_keywords.append(ent.text)

        # Extract important nouns and proper nouns
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"]:
                if token.dep_ not in ["compound"] or token.head.pos_ in ["NOUN", "PROPN"]:
                    product_keywords.append(token.text)

    # Determine the most frequent keyword as product type
    if product_keywords:
        keyword_counts = Counter(product_keywords)
        product_type = keyword_counts.most_common(1)[0][0]
    else:
        product_type = "Unknown"

    return product_type



title = "Portable Folding Stents For Samsung Galaxy S10 X 5G, Sony Xperia XZ Pro, LG Q8 Plus, Nubia Z18s, Asus Zenfone AR ZS571KL, Samsung Galaxy A70, Samsung Galaxy S10 X Multi Angle Adjustable Mobile Cell Phone Desktop Holder / portable folding stents mobile holder / universal stents mobile stand Lazy Bracket Stand Flexible Clip Mount clamp Multi Angle Stand iPhone, Android, Foldable Perfect Bed, Office, Table, Home, Gift Desktop - (A1, Mix) : Amazon.in: Electronics"
print(simplify_title(title))
#print(find_product_type(title))