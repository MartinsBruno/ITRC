def modifyHostgroupName(string):
    return string.replace(".", "-").replace(":", "-").replace("/", " - ")
