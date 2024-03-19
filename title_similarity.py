
from sentence_transformers import SentenceTransformer
from sentence_transformers import util
from fuzzywuzzy import fuzz
from utility import NormalizeString

model_s = SentenceTransformer('all-mpnet-base-v2')

text_1 = "Arya's pencil Aria model 3052 24 color pencil suitable for boys"
text_2 = "Arya's pencil color Aria color pencil model a02 12"

pre_obj = NormalizeString()
text_1_norm = pre_obj.preprocess_string(text_1)
text_2_norm = pre_obj.preprocess_string(text_2)
print("text_1_norm: ", text_1_norm)
print("text_2_norm: ", text_2_norm)

emb_1 = model_s.encode(text_1)
emb_2 = model_s.encode(text_2)

print("fuzzy_sim: ", fuzz.token_set_ratio(text_1_norm, text_2_norm))
print("sbert sim: ", util.cos_sim(emb_1, emb_2))
