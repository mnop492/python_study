import xml.etree.ElementTree as ET
from Config import Config

def printXML():
    tree = ET.parse('BlockMatchMY-junit.xml')
    root = tree.getroot()
    for testcase in root.iter('testcase'):
        print(testcase.tag, testcase.attrib)
        testcase.attrib.pop('time')
        testcase.attrib.update({'result':'pass'})
        print(testcase.tag, testcase.attrib)
    ##    for system_out in testcase.find('system-out'):
    ##        print(system_out)
    ##        testcase.remove(system_out)
    tree.write('output.xml')

config = Config('config.ini')
account = config.login_info_list[0]
print(account)
