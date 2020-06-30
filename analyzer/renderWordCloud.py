from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import os
import matplotlib
from os.path import dirname
from matplotlib.colors import LinearSegmentedColormap
class WordCloudRenderer:
    def __init__(self, d, pal):
        self.dict = dict(d)
        self.base_dir = dirname(dirname(__file__))
        self.mask_dir = '/img/wordcloud'

        self.font_dir = '/fonts/NanumSquareR.ttf'

        self.maskPic = np.array(Image.open(self.base_dir+self.mask_dir+'/mask.png'))
        self.palette= pal
        # self.colors = ["#75D701","#f9320c","#f9c00c","#0080ff",]

    def setMask(self, filename):
        self.maskPic = np.array(Image.open(filename))

    def getWordCloud(self):
                              ## NanumBarunGothic.ttf',

        # cmap = LinearSegmentedColormap.from_list("mycmap", self.colors)

        wordcloud = WordCloud(font_path='{}/{}'.format(self.base_dir,self.font_dir),\
                                  background_color="rgba(255, 255, 255, 0)", mode="RGBA",\
                                  max_font_size=120, \
                                  min_font_size=18, \
                                  mask=self.maskPic, \
                                  width=200, height=200, \
                                  colormap=self.palette)\
                        .generate_from_frequencies(self.dict)
        return wordcloud

