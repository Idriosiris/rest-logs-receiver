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
        self.sections = {}
        for var in range(1, 9):
            inclineSectionRule = re.findall(r'incline0'+str(var)+'([\s\S]*?)--------------------------------------------------------------------------------',text)
            self.sections["incline0"+str(var)] = inclineSectionRule

        inclineSectionRule = re.findall(r'incline10([\s\S]*?)--------------------------------------------------------------------------------', text)
        self.sections["incline10"] = inclineSectionRule


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
            buffersAndCacheStatsLine = re.search(r'cache:(.+)\n', section).group()
            '''This stats are not used yet'''
            upTimeStats = re.search(r'\n(.+)\n-', section).group()

            memoryStatsArray = re.findall('\d+', memoryStatsLine)
            swapStatsArray = re.findall('\d+', swapStatsLine)
            buffersAndCacheStatsArray = re.findall('\d+', buffersAndCacheStatsLine)

            self.sectionName = sectionName

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

    to_be_parse = request.get_data()
    to_be_parse = cutit(to_be_parse, 211)
    sections = Sections(to_be_parse).sections

    '''For each section found on the file we extract it's
    data and put it in the toBeReported dictionary '''
    for nodeName, section in sections.iteritems():
        if not section:
            sectionData = Data('empty', nodeName)
        else:
            sectionData = Data(section[0], nodeName)

        sectionData.reportTotalMemory()
        sectionData.reportUsedMemory()
        sectionData.reportFreeMemory()
        sectionData.reportSharedMemory()

    return 'done'
