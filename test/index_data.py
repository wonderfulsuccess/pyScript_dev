# encoding=utf-8
import jieba
import codecs

text = "学而思或者好未来的CEO在创办编程猫的初期，孙悦和李天驰开始了白天编程、晚上教书的生活，每天通过QQ给孩子们教授课程。在李天驰看来，工业时代依赖机器，而人工智能时代更依赖背后的算法，即编程"
DICT_PATH = "/Users/claire/Elasticsearch/pyScript_dev/app/analysis/"
DICT = DICT_PATH+'mydict.txt'
# jieba.load_userdict('mydict.txt')
jieba.load_userdict(DICT)

seg_list = jieba.cut(text, cut_all=True)
print("Full Mode: " + "/ ".join(seg_list))  # 全模式
