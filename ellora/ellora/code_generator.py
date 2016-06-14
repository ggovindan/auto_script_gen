
class CodeGenerator:
    def __init__(self, indentation='\t'):
        self.indentation = indentation
        self.level = 0
        self.code = ''

    def indent(self):
        self.level += 1

    def dedent(self):
        if self.level > 0:
            self.level -= 1
            
    def classMethodIndent(self):
        self.level = 1

    def methodIndent(self):
        self.level = 2
        
    def __add__(self, value):
        temp = CodeGenerator(indentation=self.indentation)
        temp.level = self.level
        temp.code = str(self) + ''.join([self.indentation for i in range(0, self.level)]) + str(value) + "\n"
        return temp

    def __str__(self):
        return str(self.code)

#a = CodeGenerator()
#a += 'for a in range(1, 3):'
#a.indent()
#a += 'for b in range(4, 6):'
#a.indent()
#a += 'print(a * b)'
#a.dedent()
#a += '#pointless comment'
#print(a)


#This test covers the automatable Hybrid Lobby Screen Tests. Verify using single/multi stream & conference state. welcomeScreen =True

#(1) Every participant should see lobby screen (dial in and out)

#Lobby screen goes away after 5 sec when video start flowing

#(2) Lobby screen with only 1 participant left in meeting

#(3) Lobby screen with PIN Entry

#Lobby screen goes away after PIN Entry

#(4) Every participant should see lobby screen (guest and chair)

#Lobby screen goes away after chair

#(5) Lobby screen during Remote Hold

#Lobby screen goes away after resume



#TestcaseInvolvesThirdParty = False
#testNumber = 1234567
#if 1 or TestcaseInvolvesThirdParty:
#    parentclass = "remotelyManagedTestcase"

#a = CodeGenerator()
#a += FindImports(a)
#a += "class TestWhatEver(%s):" % (parentclass)
#a.indent()
#a += "test_id = %d" % (testNumber)
#a += "resources = {"
#a += "\'dut\': hybrid_ts,"
#a += "\'endpoint1\': multistream_endpoint,"
#a += "\'endpoint2\': multistream_endpoint,"
#a += "\'endpoint3\': multistream_endpoint,"
#a += "}\n"

#print(a)

