# 详细设置参见文档 https://coloredlogs.readthedocs.io/en/latest/#changing-the-log-format
# export COLOREDLOGS_LOG_FORMAT='%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s'
import coloredlogs,logging

logger = logging.getLogger(__name__)

coloredlogs.install(level='DEBUG')

logger.debug("this is a debugging message")
logger.info("this is an informational message")
logger.warning("this is a warning message")
logger.error("this is an error message")
logger.critical("this is a critical message")