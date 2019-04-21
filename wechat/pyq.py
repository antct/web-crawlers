import re
import time
import os
import requests

class pyq():
    def __init__(self, mask='Male'):
        self.src = r'./exported_sns.json'
        self.text_url = r'./content.txt'
        self.mask_url = './word/alice_mask.png' if mask == "Female" else './word/boy_mask.png'
        self.font_url = r'./word/SourceHanSans-Regular.otf'
        self.target = r'./temp.png'


    def segment(self):
        print("[%s] start to segment" % (time.ctime(time.time())))

        raw_content = []
        with open('./exported_sns.json', encoding='utf-8') as f:
            raw_content = eval(f.read().replace("false", "False").replace("true", "True"))

        content = [item['content'] for item in raw_content]
        with open('./content.txt', mode='w+', encoding='utf-8') as wf:
            for con in content:
                # replace #
                con, number = re.subn('[#]', "", con)
                # replace [emoji]
                con, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", con)
                wf.write(con)
        print("[%s] segment ok" % (time.ctime(time.time())))


    def get_pyq_word_cloud(self):
        import jieba
        from scipy.misc import imread
        from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

        print("[%s] start to generate word cloud" % (time.ctime(time.time())))
        try:
            with open(self.text_url, encoding='utf-8') as f:
                all_chaps = [chap for chap in f.readlines()]
        except Exception as e:
            print("[%s] make sure content.txt exists" % (time.ctime(time.time())))
            print(e)

        dictionary = []
        for i in range(len(all_chaps)):
            words = list(jieba.cut(all_chaps[i]))
            dictionary.append(words)

        # flat
        tmp = []
        for chapter in dictionary:
            for word in chapter:
                tmp.append(word.encode('utf-8'))
        dictionary = tmp

        # filter
        unique_words = list(set(dictionary))

        freq = []
        for word in unique_words:
            freq.append((word.decode('utf-8'), dictionary.count(word)))

        # sort
        freq.sort(key=lambda x: x[1], reverse=True)

        # broke_words
        broke_words = []

        try:
            with open('word/stopwords.txt') as f:
                broke_words = [i.strip() for i in f.readlines()]
        except Exception as e:
            broke_words = STOPWORDS

        # remove broke_words
        freq = [i for i in freq if i[0] not in broke_words]

        # remove monosyllable words
        freq = [i for i in freq if len(i[0]) > 1]

        img_mask = imread(self.mask_url)
        img_colors = ImageColorGenerator(img_mask)

        wc = WordCloud(background_color="white",  # bg color
                    max_words=2000,  # max words
                    font_path=self.font_url,
                    mask=img_mask,  # bg image
                    max_font_size=60,  # max font size
                    random_state=42)

        wc.fit_words(dict(freq))

        wc.to_file(self.target)

        


