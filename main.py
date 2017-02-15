from flask import Flask
from flask import request
from parser import Data
from parser import Sections
from statsd import StatsClient
statsd = StatsClient(host='localhost',
                     port=8125,
                     prefix=None,
                     maxudpsize=512,
                     ipv6=False)
app = Flask(__name__)

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
