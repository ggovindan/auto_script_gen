import simplejson
from code_generator import CodeGenerator

def main(filename, execute):
    try:
        print "filename=", filename
        prefix= filename.split(".")[0]
        output_file_name = prefix + ".py"
        output = open(output_file_name, 'w')    
        f = open(filename, "r")
        data = simplejson.load(f)
        data = byteify(data)
        
        codegen = CodeGenerator()
        #name the testcase
        codegen = identify_imports(data, codegen)
        codegen += ""
        codegen += ""
        codegen += "class Test7777777(%s):" % (IdentifyParentClasses(data))
        codegen.indent()
        codegen += "test_id = 7777777"
        codegen = identify_resources(data, codegen)
        codegen = createSetupMethod(data, codegen)
        codegen = createRunMethod(data, codegen)
    
        output.write(str(codegen))
        return str(codegen)
    except:
        raise 
    

    
        
def identify_imports(data, codegen):
    '''This needs to scan through all the resources and the actions in the testcase and identify
    the import file. In the general case we will want to import remotelymanagedtestcase and SIP and TCP in order
    to setup the endpoints for dialing and general helper functions from files.
    This will need more parsing of the JSON file and coming up with the list. For now just importing the important ones
    '''
    codegen += "from testcases.remotelyManagedTestcase import remotelyManagedTestcase"
    codegen += "from common_resources import multistream_endpoint, hybrid_ts, ipv4, ipv6, pse_performance_clips, callinator_separate_hardware, any_ts, registrar"
    #codegen += "from analyse_pcap import count_mari_reports_for_cascade_link"
    #codegen += "from analyse_bluebox import checkLobbyScreen"
    codegen += "from endpointapi.constants import CALL_PROTOCOL_SIP, SIP_TRANSPORT_TCP"
    codegen += "import time"
    codegen += "import re"
    return codegen

def identify_resources(data, codegen):
    codegen += "resources = {\n"
    try:
        for stmts in data:
            if "resources" in stmts.keys():
                print "found the resources JSON"
                for key, val in stmts['resources'].iteritems():
                    codegen += "\'%s\': %s," % (key, val)
                codegen += "}"
                return codegen
        raise ValueError("resource command not found")        
    except ValueError:
        print "Resources json command is mandatory for every testcase"
        raise

def createSetupMethod(data, codegen):
    '''This method needs to do parse through the test procedure and find out if there are any CUCM/VCS to be setup
    and then register those. For now we will just do default things like 
    1. install encryption certificate 
    2. install advance diagnostics certificate
    '''
    print "create setup method.."
    codegen += ""
    codegen.classMethodIndent()
    codegen += "def setup(self):"
    codegen.indent()
    
    codegen += ""
    codegen += "for e in self.endpoints:"
    codegen.indent()
    codegen += "e.sip.defaultTransport = SIP_TRANSPORT_TCP"
    codegen += "e.multistreamConfig.enabled = True"
    codegen += "e.autoAnswer = True"
    codegen += "self.endpoint_uri = self.setupEndpointRegistration('sip', self.vcs, e, sipTransport='tcp')"

    codegen.dedent()

    codegen += "for dut in self.all_blueboxes:"
    codegen.indent()
    codegen += "dut.webapi.settings.sip.setRegistrar(transport=\'tcp\')"
    codegen += "dut.webapi.settings.upgrade.addAdvancedDiagnosticsKey()"
    codegen += "dut.webapi.settings.upgrade.addEncryptionKey()"
    #codegen += "self.setupBlueboxRegistration('sip', self.vcs, box=dut, sipTrunk=True, sipDomain=\"de-vcs-hybrid-ts\")"
        # set up a trunk from the VCS so we can dial in
    #codegen += "self.prefix = self.setupTrunk(self.vcs, box=dut, h323Enabled=False)"
    return codegen

def createRunMethod(data, codegen):
    '''This method needs to parse through the test procedure and then start writing code
     for each of the commands in the same sequence
    '''
    print "create run method"
    codegen += ""
    codegen.classMethodIndent()
    codegen += "def run(self):"
    codegen += ""
    codegen.indent()
    for stmts in data:
        if "action" in stmts.keys():
            codegen = supported_actions[stmts['action']](stmts, codegen)
    return codegen
            
def IdentifyParentClasses(data):
    '''For now the default parent class is remotelyManagedTestcase
       going further we will have to identify from the resources json and the other actions to identify 
       if each testcase needs to be derived from multiple testcases
    '''
    return "remotelyManagedTestcase"
            

def load_app_image(stmts):
    try:
        output.write("from upload_app import upload_app\n")
        ipaddr = "ipaddr = [\'" +stmts['server_ip']+ "\']\n"
        output.write(ipaddr)
        output.write("upload_app(ipaddr)")
    except KeyError:
        print "mandatory field is missing{}".format(stmts)
        raise
    except:
        raise

def create_conference(stmts, codegen):
    print "writing code to create conference..."
    try:
        codegen += "#creating default conference..."
        codegen += "self.uri = \'1\'"
        codegen += "conferenceID = self.%s.api.flex.conference.create_default(" % (stmts['serverName'])
        codegen.indent()
        strPin = ""
        if "PIN" in stmts.keys():
            strPin = "\'PIN\': \'%s\'" % (stmts['PIN'])
        codegen += "self.conference_name, URIs=[{'URI': self.uri, 'callBandwidth': 40000000, %s}]" % (strPin)
        codegen.dedent()
        codegen += ")['conferenceID']"
        return codegen
    except KeyError:
        print "serverName(same as resource key) is mandatory for conference create"
        raise
    
def dial_dtmf(stmts, codegen):
    try:
        codegen += ""
        #self.endpoint1.dtmf('6666#')
        codegen += "self.%s.dtmf(\'%s#\')" % (stmts['PIN'])
        return codegen
    except KeyError:
        print "PIN in mandatory for dial_dtmf{}".format(stmts)
        raise

def dial_out_ep(stmts, codegen):
    print "Writing code to call endpoint"
    try:
        codegen += ""
        codegen += "#code to dial out endpoint"
        codegen += "conflist = self.%s.api.flex.conference.enumerate()[\'conferences\']" % (stmts['serverName'])
        codegen += "for conf in conflist:"
        codegen.indent()
        codegen += "if conf[\'conferenceName\'] == self.conference_name"
        codegen.indent()
        codegen += "confid = conf[\'conferenceID\']"
        codegen += "break"
        codegen.dedent()
        codegen.dedent()

        codegen += ""
        codegen += "callOutParams = {"
        codegen.indent()
        codegen += "\'conferenceID\': confid,"
        codegen += "\'calls\': [{\'remoteAddress\': self.%s.ip, \'protocol\': \'sip\', \'callBandwidth\': 4000000}]," % (stmts['epName'])
        codegen.dedent()
        codegen += "}"
        codegen += "call1, _ = self.%s.receiveCallAndConnect(self.%s.api.flex.participant.create, None, callOutParams)" % (stmts['epName'], stmts['serverName'])
        
        #another way to do it !!
        #codegen += "self.%s.api.flex.participant.create(" % (stmts['serverName'])
        #codegen.indent()
        #codegen += "calls=[{\'protocol\': \'sip\', \'callBandwidth\': 4096000, \'remoteAddress\':%s.ip},],conferenceID=confid,)" % (stmts['epName'])
        #codegen.dedent()
        return codegen
    except KeyError:
        raise Exception("serverName, confName and epName(same as resource key) is mandatory for dial_out_ep{}".format(stmts))

    
def dial_in_ep(stmts, codegen):
    print "writing code to dial in endpoint"
    try:
        codegen += ""
        codegen += "#Dial in an endpoint"
        codegen += "conflist = self.%s.api.flex.conference.enumerate()[\'conferences\']" % (stmts['serverName'])
        codegen += "for conf in conflist:"
        codegen.indent()
        codegen += "if conf[\'conferenceName\'] == self.conference_name"
        codegen.indent()
        codegen += "confid = conf[\'conferenceID\']"
        codegen += "break"
        codegen.dedent()
        codegen.dedent()
        codegen += ""
        codegen += "self.%s.dialAndConnect(confid, CALL_PROTOCOL_SIP)" % (stmts['epName'])
        return codegen
    except KeyError:
        raise Exception("serverName, confName and epName(same as resource key) is mandatory for dial_out_ep{}".format(stmts))
    
def wait(stmts, codegen):
    try:
        
        codegen += ""
        codegen += "self.wait(%d)" % (int(stmts['time']))
        return codegen
    except KeyError:
        raise Exception("time is mandatory for wait".format(stmts))

def hangup(stmts, codegen):
    try:
        codegen += ""
        codegen += "for call in self.%s.calls:" % (stmts['epName'])
        codegen.indent()
        codegen += "call.hangUpAndDisconnect()"
        codegen.dedent()
        return codegen
    except KeyError:
        raise Exception( "epName is mandatory for hangup")
    
def destroy_conference(stmts, codegen):
    try:
        codegen += ""
        codegen += "#destroy the conference"
        codegen += "confid = \'\'"
        codegen += "conflist = self.%s.api.flex.conference.enumerate()[\'conferences\']" % (stmts['serverName'])
        codegen += "for conf in conflist:"
        codegen.indent()
        codegen += "if conf[\'conferenceName\'] == \'%s\':" % (stmts['confName'])
        codegen.indent()
        codegen += "confid = conf[\'conferenceID\']"
        codegen += "break"
        codegen.dedent()
        codegen.dedent()
        codegen += "self.%s.api.flex.conference.destroy(confid)" % (stmts['serverName'])
        return codegen
    except KeyError:
        raise Exception( "serverName, confName are mandatory for destroy_conference")
        
def verify_lobby_screen(stmts, codegen):
    try:
        codegen += ""
        codegen += "#verify lobby screen"
        codegen += "try:"
        codegen.indent()
        codegen += "pid = \'\'"
        codegen += "for call in self.%s.calls:" % (stmts['epName'])
        codegen.indent()
        codegen += "pid = call.participant_id"
        codegen.dedent()
        codegen += "if pid == \'\':"
        codegen.indent()
        codegen += "raise ValueError(\"participant id is not found in endpoint\")"
        codegen.dedent()
        codegen.dedent()
        codegen += "except ValueError:"
        codegen.indent()
        codegen += "raise"
        codegen.dedent()
        codegen += "msgSuccess, msgFailure = checkLobbyScreen(pid, self.%s, %s, \'%s\', \'%s\')" % (stmts['serverName'], stmts['SSExpected'], stmts['expectedState'], stmts.get("scenario"))
        codegen += "self.result.addSuccess(msgSuccess)"
        #codegen += "self.result.addFailure(msgFailure)"
        return codegen
    except KeyError:
        raise Exception( "epName, SSExcepted(True, False), expectedState are mandatory. scenario(scenario before executing this test) is optional {}".format(stmts))
        
            
        
def load_kupgrade(stmts):
    try:
        print "upload kupgrade"
        mystr = "from upload_kupgrade import upload_kupgrade_file\nimport os\n\n"
        output.write(mystr)
        mystr = "import myexport\n"\
        "image_location=myexport.download_release_build(\'%s\',\'%s\',\'%s\', \'%s\')\n\n" % (stmts['release_name'], stmts['build_no'], stmts['target'], stmts['binary_type'])
        output.write(mystr)
        mystr = "image_location = os.getcwd() + \'/\' + image_location + \'/\' + \'cisco_ts_media_300.kupgrade\'\n\n"
        output.write(mystr)
        mystr = "upload_kupgrade_file(%s, image_location)\n" % (stmts['server_ips'])
        output.write(mystr)
    except KeyError:
        print "server_ips, release_name, build_no, target, binary_type  are mandatory for load_kupgrade{}".format(stmts)
        raise
  
def participant_create(stmts, codegen):
    print "Creating cascade link"
    try:
        codegen += ""
        codegen += "#Create a participant on a dut"
        codegen += "confid = \'\'"
        codegen += "conflist = self.%s.api.flex.conference.enumerate()[\'conferences\']" % (stmts['serverName'])
        codegen += "for conf in conflist:"
        codegen.indent()
        codegen += "if conf[\'conferenceName\'] == self.conference_name:"
        codegen.indent() 
        codegen += "confid = conf[\'conferenceID\']"
        codegen += "break"
        codegen.dedent()
        codegen.dedent()
        codegen += "cascade_participant = self.%s.api.flex.participant.create(" % (stmts['serverName'])
        codegen.indent()
        #codegen += "calls=[{\'uri\': \'{}{}\'.format('{}z'.format(self.%s.uid()), self.uri+'1'), \'callBandwidth\': 4096000, }," % (stmts['slaveName'])
        codegen += "calls=[{\'uri\': \'2\', \'callBandwidth\': 4096000, },"
        codegen += "],\nconferenceID=confid,"
        codegen += "cascadeRole=\'%s\',)" % (stmts['cascadeRole'])
        codegen += ""
        codegen.dedent()
        return codegen
    except KeyError:
        raise Exception( "serverName(same as resource name), cascadeRole(cascadeMaster/cascadeSlave/None),  are mandatory {}".format(stmts))
    
def participant_dial(stmts, codegen):
    try:
        codegen += "#dial out a participant"
        codegen += "confid = \'\'"
        codegen += "conflist = self.%s.api.flex.conference.enumerate()[\'conferences\']" % (stmts['serverName'])
        codegen += "for conf in conflist:"
        codegen.indent()
        codegen += "if conf[\'conferenceName\'] == self.conference_name:"
        codegen.indent() 
        codegen += "confid = conf[\'conferenceID\']"
        codegen += "break"
        codegen.dedent()
        codegen.dedent()
        codegen += "cascade_link = self.%s.api.flex.participant.create(" % (stmts['serverName'])
        codegen.indent()
        codegen += "calls=[\n"
        #codegen += "{\'protocol\': \'sip\', \'callBandwidth\': 4096000, \'remoteAddress\': \'{}{}\'.format('{}z'.format(self.%s.uid()), self.uri+'1'),}," % (stmts['masterName'])
        codegen += "{\'protocol\': \'sip\', \'callBandwidth\': 4096000, \'remoteAddress\': \"{}@{}\".format(\'2\', self.%s.ip),}," % (stmts['remoteServerName'])
        codegen += "],"
        codegen += "conferenceID=confid,"
        codegen += "cascadeRole=\'%s\',)" % (stmts['cascadeRole'])
        codegen.dedent()
        return codegen
    except KeyError:
        raise Exception( "serverName(same as resource name), remoteServerName(remote TS to dial to), cascadeRole(cascadeMaster/cascadeSlave/None),  are mandatory {}".format(stmts))
    
def verify_call_count(stmts, codegen):
    try:
        codegen += ""
        codegen += "#verify the call count on a dut"
        codegen += "msgSuccess = \"\""
        codegen += "msgFailure = \"\""        
        codegen += "callCount=0"
        codegen += "participantList = self.%s.api.flex.participant.enumerate()['participants']" % (stmts['serverName'])
        codegen += "for part in participantList:"
        codegen.indent()
        codegen += "callid=part.get(\'callID\')"
        codegen += "if callid == None:"
        codegen.indent()
        codegen += "continue"
        codegen.dedent()
        codegen += "else:"
        codegen.indent()
        codegen += "callCount+=1"
        codegen.dedent()
        codegen.dedent() # for part in participantlist
        codegen += "if callCount == {}:".format(stmts['expectedCount'])
        codegen.indent()
        codegen += "msgSuccess = \'{} scenario number of calls={}\'.format(\'%s\', callCount)" % (stmts['scenario'])
        codegen += "self.result.addSuccess(msgSuccess)"
        codegen.dedent()
        codegen += "else:"
        codegen.indent()
        codegen += "msgFailure = \'{} scenario number of calls={}\'.format(\'%s\', callCount)" % (stmts['scenario'])
        codegen += "self.result.addFailure(msgFailure)"
        codegen.dedent()
        return codegen
    except KeyError:
        raise Exception("serverName(same as resource name) where the call count needs to be verified is mandatory{}".format(stmts))
    
def check_eventlog(stmts, codegen):
    try:
        codegen +=""
        codegen +="self.wait(6)"
        codegen += "foundError=False"
        codegen += "for event in self.%s.webapi.logs.event_log.getall()['logs']:" % (stmts['serverName'])
        codegen.indent()
        codegen += "if event[\'severity\'] == \'%s\':" %(stmts['severity'])
        codegen.indent()
        codegen += "if re.search(\'%s\', event[\'message\']):" % (stmts['message'])
        codegen.indent()
        codegen += "foundError = True"
        codegen += "self.result.addSuccess(\'{} message found\'.format(event[\'message\']))"
        codegen += "break"
        codegen.dedent()
        codegen.dedent()
        codegen.dedent()
        codegen += "if foundError==False:"
        codegen.indent()
        codegen += "self.result.addFailure(\'{} message was not found\'.format(\'%s\'))" % (stmts['message'])
        codegen.dedent()
        return codegen
    except KeyError:
        raise Exception("serverName(same as resource name) severity(Error/Warning/Info) message(message to search in the log file) are mandatory{}".format(stmts))
        
def create_cascade(stmts, codegen):
    print "Creating cascade link"
    try:
        codegen += ""
        codegen += "#create entire cascade"
        codegen += "confid = \'\'"
        codegen += "conflist = self.%s.api.flex.conference.enumerate()[\'conferences\']" % (stmts['slaveName'])
        codegen += "for conf in conflist:"
        codegen.indent()
        codegen += "if conf[\'conferenceName\'] == self.conference_name:"
        codegen.indent() 
        codegen += "confid = conf[\'conferenceID\']"
        codegen += "break"
        codegen.dedent()
        codegen.dedent()
        codegen += "cascade_participant = self.%s.api.flex.participant.create(" % (stmts['slaveName'])
        codegen.indent()
        #codegen += "calls=[{\'uri\': \'{}{}\'.format('{}z'.format(self.%s.uid()), self.uri+'1'), \'callBandwidth\': 4096000, }," % (stmts['slaveName'])
        codegen += "calls=[{\'uri\': \'2\', \'callBandwidth\': 4096000, },"
        codegen += "],\nconferenceID=confid,"
        codegen += "cascadeRole=\'cascadeSlave\',)"
        codegen += ""
        codegen.dedent()
    
        codegen += ""
        codegen += "conflist = self.%s.api.flex.conference.enumerate()[\'conferences\']" % (stmts['masterName'])
        codegen += "for conf in conflist:"
        codegen.indent()
        codegen += "if conf[\'conferenceName\'] == self.conference_name:"
        codegen.indent() 
        codegen += "confid = conf[\'conferenceID\']"
        codegen += "break"
        codegen.dedent()
        codegen.dedent()
        codegen += "cascade_link = self.%s.api.flex.participant.create(" % (stmts['masterName'])
        codegen.indent()
        codegen += "calls=[\n"
        #codegen += "{\'protocol\': \'sip\', \'callBandwidth\': 4096000, \'remoteAddress\': \'{}{}\'.format('{}z'.format(self.%s.uid()), self.uri+'1'),}," % (stmts['masterName'])
        codegen += "{\'protocol\': \'sip\', \'callBandwidth\': 4096000, \'remoteAddress\': \"{}@{}\".format(\'2\', self.%s.ip),}," % (stmts['slaveName'])
        codegen += "],"
        codegen += "conferenceID=confid,"
        codegen += "cascadeRole=\'cascadeMaster\',)"
        codegen.dedent()
        return codegen
    except KeyError:
        raise Exception( "masterName, slaveName,  are mandatory {}".format(stmts))

def start_and_download_pcap(stmts, codegen):
    print "code to start pcap and download it for analysis"
    try:
        codegen +=""
        codegen += "self.%s.webapi.status.deleteNetworkCapture()\n" % (stmts['serverName'])
        codegen += "self.%s.webapi.status.networkCaptureStart()\n" % (stmts['serverName'])
        codegen += "time.sleep(%d)\n" % (int(stmts['duration']))
        codegen += "self.%s.webapi.status.networkCaptureStop()"
        codegen += "self.%s.webapi.status.downloadNetworkCapture(\'/root/automation/dipoza.pcap\')\n" % (stmts['serverName'])
        return codegen
    except KeyError:
        raise Exception( "serverName, duration are mandatory fields{}".format(stmts))

def analyze_pcap(stmts, codegen):
    print "Analysing pcap"
    try:
        if stmts['analysis_type'] == 'count_mari_reports':
            codegen += ""
            codegen += "count_mari_reports_for_cascade_link(%s.ip, %s.ip)\n" % (stmts['sourceServerName'], stmts['destnServername'])
            return codegen
        else:
            print "analysis_type(%s) is not yet supported" % (stmts['analysis_type'])
    except KeyError:
        raise Exception( "sourceServername, destnServername and analysis_type are mandatory{}".format(stmts))
     
def download_image(stmts):
    print "download_image"
    try:
        mystr = "import myexport\n"\
        "myexport.download_release_build(\'%s\',\'%s\',\'%s\', \'%s\')\n\n" % (stmts['release_name'], stmts['build_no'], stmts['target'], stmts['binary_type'])
        output.write(mystr)
    except KeyError:
        print "release_name(waterloo/westminster/wowbagger), build_no, target(arthur/wowbagger/centos/vogon/ash.amd64), binary_type(kupgrade/ova-devel/zupgrade/rpm) are mandatory"
        raise 
    
def hold_resume(stmts, codegen):
    print "hold_resume"
    try:
        codegen += ""
        codegen += "for call in self.%s.calls:" % (stmts['epName'])
        hold_resume = stmts['what']
        codegen.indent()
        codegen += "call.%s()" % (hold_resume)
        codegen.dedent()
        return codegen
    except KeyError:
        raise Exception( "epName, what(hold or resume) are mandatory{}".format(stmts))
     

def enable_encryption(stmts):
    print "setting up encryption"

 
supported_actions = {'load_app_image': load_app_image, 
                     'create_conference': create_conference, 
                     'dial_out_ep': dial_out_ep,
                     'load_kupgrade': load_kupgrade,
                     'create_cascade': create_cascade, 
                     'download_pcap': start_and_download_pcap,
                     'analyze_pcap': analyze_pcap, 
                     'download_image': download_image,
                     'enable_encryption': enable_encryption,
                     'dial_in_ep': dial_in_ep,
                     'hangup': hangup,
                     'destroy_conference': destroy_conference,
                     'verify_lobby_screen': verify_lobby_screen,
                     'wait': wait,
                     'hold_resume': hold_resume,
                     'participant_create': participant_create,
                     'participant_dial': participant_dial,
                     'verify_call_count': verify_call_count,
                     'check_eventlog': check_eventlog,
                    }

def byteify(jsoninput):
    if isinstance(jsoninput, dict):
        return {byteify(key):byteify(value) for key,value in jsoninput.iteritems()}
    elif isinstance(jsoninput, list):
        return [byteify(element) for element in jsoninput]
    elif isinstance(jsoninput, unicode):
        return jsoninput.encode('utf-8')
    else:
        return jsoninput

