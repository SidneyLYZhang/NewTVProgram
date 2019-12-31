import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import jieba
from PIL import Image
import click


@click.command()


icon = Image.open("E:/book.png").convert("RGBA")
mask = Image.new("RGB", icon.size, (1200,1200,1200))
mask.paste(icon,icon)
amazon_coloring = np.array(mask)
wordlist_after_jieba = jieba.cut(emotions, cut_all = True)
wl_space_split = " ".join(wordlist_after_jieba)
my_wordcloud = WordCloud(font_path="C:/Windows/Fonts/sarasa-term-sc-regular.ttf",background_color="white",max_words=2000,max_font_size=50,mask=amazon_coloring).generate(wl_space_split)
my_wordcloud.to_file("E:/test_cloud_book_0.jpg")
