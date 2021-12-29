import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s %(filename)s:%(lineno)d] %(message)s')

def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的item的name和nodeid的中文显示在控制台上
    :return:
    """
    for item in items:
        # 只需要对中括号内的数据做一个编码转换即可，防止因为测试用例本身就是中文导致编码再出问题
        names = item.name.split("[")
        nodeids = item.nodeid.split("[")
        if len(names) > 1:
            item.name = names[0] + "[" + names[-1].encode("utf-8").decode("unicode_escape")
        if len(nodeids) > 1:
            # 报告里用例名称用的是nodeis所以nodeid也需要转换一下
            item._nodeid = nodeids[0] + "[" + nodeids[-1].encode("utf-8").decode("unicode_escape")