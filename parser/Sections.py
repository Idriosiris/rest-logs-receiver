import re
class Sections:
    def __init__(self, text):
        self.sections = {}
        for var in range(1, 9):
            inclineSectionRule = re.findall(r'incline0'+str(var)+'([\s\S]*?)--------------------------------------------------------------------------------',text)
            self.sections["incline0"+str(var)] = inclineSectionRule

        inclineSectionRule = re.findall(r'incline10([\s\S]*?)--------------------------------------------------------------------------------', text)
        self.sections["incline10"] = inclineSectionRule