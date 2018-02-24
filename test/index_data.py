# 详细设置参见文档 https://coloredlogs.readthedocs.io/en/latest/#changing-the-log-format
# export COLOREDLOGS_LOG_FORMAT='%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s'
# export COLOREDLOGS_LOG_FORMAT='%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'
import coloredlogs,logging
import requests

import re

logger = logging.getLogger(__name__)

coloredlogs.install(level='critical')

logger.debug("this is a debugging message")
logger.info("this is an informational message")
logger.warning("this is a warning message")
logger.error("this is an error message")
logger.critical("this is a critical message")


# for page in range(0,10):
#     url='http://www.guandian.cn/api.php?op=getindex2016_content&modelid=1&type=query-scroll&a='+str(page)
#     r = requests.get(url)
#     print(r.status_code)


# ip = requests.get("http://api.ip.data5u.com/dynamic/get.html?order=5135da4a4ce8e4a4848474ab8c3d7a79&sep=0").text
# print(ip)

s='果然，这一年基础零售经历为赵奎铭现在的工作积累了零售终端的经验。2009年，他加入捷成集团，先是做了保时捷设计的品牌经理，又通过集团内部选拔应聘成为杭州西湖保时捷中心销售经理—在捷成代理的众多品牌里，保时捷占了很重要的比重。  现在，赵奎铭正啃着MBA课本，希望为将来向管理和战略层面的职业发展做积累。  ![](https://files.cbnweek.com/728e5f51ded36d56c706bdeaeaab85ac_374x500.jpeg)  **个人档案**  姓名：赵奎铭  星座：狮子座  学历：英属哥伦比亚大学心理学 本科  英属哥伦比亚大学MBA 在读  职业：杭州西湖保时捷中心销售经理  **C=CBNweekly**   **Z=Zhao Kuiming**  **C：学心理学专业的时候'
p_zh = "[^/!.+?^/)]"
pattern_zh = re.compile(p_zh)
source_text = ''.join(pattern_zh.findall(s))
print(source_text)