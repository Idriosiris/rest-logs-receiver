import sys
import json, ast
import re
import pyparsing as pp
from flask import Flask
from flask import request
from statsd import StatsClient

statsd = StatsClient(host='localhost',
                     port=8125,
                     prefix=None,
                     maxudpsize=512,
                     ipv6=False)

app = Flask(__name__)


class Sections:
    def __init__(self, text):
        first = pp.Word("\n\nincline" + pp.nums)
        numbersAndLettersAndSpaces = pp.Word(pp.alphanums + " " + ":" + "\n" + "." + ",")
        last = pp.Word("\n--------------------------------------------------------------------------------")
        identifier = pp.OneOrMore(pp.Combine(first + numbersAndLettersAndSpaces + last) ^ pp.Combine(
            pp.Word("\n--------------------------------------------------------------------------------")))

        self.sections = self.test(text, identifier)

    def test(self, text, identifier):
        try:
            result = identifier.parseString(text)
            return result
        except pp.ParseException as x:
            print "  No match: {0}".format(str(x))


class Data:
    def __init__(self, section='empty', sectionName='incline'):
        if (section == 'empty'):
            self.sectionName = sectionName

            self.totalMemory = -1
            self.usedMemory = -1
            self.freeMemory = -1
            self.sharedMemory = -1
            self.buffersMemory = -1
            self.cachedMemory = -1

            self.usedCacheAndBuffers = -1
            self.freeCacheAndBuffers = -1

            self.totaSwap = -1
            self.usedSwap = -1
            self.freeSwap = -1

        else:
            memoryStatsLine = re.search(r'Mem:(.+)\n', section).group()
            swapStatsLine = re.search(r'Swap:(.+)\n', section).group()
            buffersAndCacheStatsLine = re.search(r'buffers\sand\scache:(.+)\n', section).group()
            '''This stats are not used yet'''
            upTimeStats = re.search(r'\n(.+)\n-', section).group()

            memoryStatsArray = re.findall('\d+', memoryStatsLine)
            swapStatsArray = re.findall('\d+', swapStatsLine)
            buffersAndCacheStatsArray = re.findall('\d+', buffersAndCacheStatsLine)

            self.sectionName = re.search(r'incline(\d+)', section).group()

            self.totalMemory = memoryStatsArray[0]
            self.usedMemory = memoryStatsArray[1]
            self.freeMemory = memoryStatsArray[2]
            self.sharedMemory = memoryStatsArray[3]
            self.buffersMemory = memoryStatsArray[4]
            self.cachedMemory = memoryStatsArray[5]

            self.usedCacheAndBuffers = buffersAndCacheStatsArray[0]
            self.freeCacheAndBuffers = buffersAndCacheStatsArray[1]

            self.totaSwap = swapStatsArray[0]
            self.usedSwap = swapStatsArray[1]
            self.freeSwap = swapStatsArray[2]

    def reportTotalMemory(self):
        entryName = self.sectionName + '.totalMemory'
        statsd.gauge(entryName, self.totalMemory)

    def reportUsedMemory(self):
        entryName = self.sectionName + '.usedMemory'
        statsd.gauge(entryName, self.usedMemory)

    def reportFreeMemory(self):
        entryName = self.sectionName + '.freeMemory'
        statsd.gauge(entryName, self.freeMemory)

    def reportSharedMemory(self):
        entryName = self.sectionName + '.sharedMemory'
        statsd.gauge(entryName, self.sharedMemory)



@app.route('/show', methods=['POST'])
def parse():
    def cutit(s, n):
        return s[n:]
    '''This dictionary holds a watch on what nodes are present in this report.
    By default all the nodes are set to 0 [not present]'''
    toBeReported = {
        'incline01': 0,
        'incline02': 0,
        'incline03': 0,
        'incline04': 0,
        'incline05': 0,
        'incline06': 0,
        'incline07': 0,
        'incline08': 0,
        'incline09': 0,
        'incline10': 0
    }

    to_be_parse = request.get_data()

    to_be_parse = cutit(to_be_parse, 211)

    to_be_parse2 = request.form.to_dict()
    '''to_be_parse2 = ast.literal_eval(json.dumps(to_be_parse2))['file']'''
    sections = Sections(to_be_parse).sections
    print sections

    '''print sections'''
    '''For each section found on the file we extract it's
    data and put it in the toBeReported dictionary '''
    '''for section in sections:
        sectionData = Data(section)
        toBeReported[sectionData.sectionName] = sectionData

    for nodeName, section in toBeReported.items():
        if section == 0:
            section = Data('empty', nodeName)
            section.reportTotalMemory()
            section.reportUsedMemory()
            section.reportFreeMemory()
            section.reportSharedMemory()

        else:
            section.reportTotalMemory()
            section.reportUsedMemory()
            section.reportFreeMemory()
            section.reportSharedMemory()

    print toBeReported'''

    return 'done'
