import spacy
from spacy_layout import spaCyLayout
import pandas as pd
from utils_ocr import ocrAnuario

nlp = spacy.load("pt_core_news_sm")
layout = spaCyLayout(nlp)

pdfFile = '../files/Cultivar Máquinas 258 - Anuario_compressed-1.pdf'
planilha = '../anuario.xlsx'
ocrAnuario(pdfFile,planilha)
