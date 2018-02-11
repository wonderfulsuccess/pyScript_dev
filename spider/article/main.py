from scrapy import cmdline
cmdline.execute("scrapy crawl jingmeiti".split())


# import subprocess

# failed_maga=[1,2]

# # for i in range(1,486):
# for i in failed_maga:
#     f = open("./temp.txt", "w", encoding='UTF-8')
#     f.seek(0)
#     f.write(str(i))
#     f.close()
#     subprocess.call("sudo python main.py "+str(i), shell=True)

# print("################## Finish ##################")