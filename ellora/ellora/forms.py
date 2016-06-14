from django import forms

class JsonTestForm(forms.Form):
    default_val = """ [{"resources": {"dut": "any_ts", "endpoint1": "multistream_endpoint", "endpoint2": "multistream_endpoint"}},

{"action": "create_conference", "serverName": "dut", "conferenceName": "GURU_SLAVE_TS"},

{"action": "dial_out_ep", "serverName": "dut", "confName": "GURU_SLAVE_TS", "epName": "endpoint1"},
{"action": "dial_out_ep", "serverName": "dut", "confName": "GURU_SLAVE_TS", "epName": "endpoint2"},
{"action": "wait", "time": "6"},
{"action": "verify_lobby_screen", "serverName": "dut", "epName": "endpoint1", "SSExpected": "False", "scenario": "dial 2 ep and check multistream after 5 secs", "expectedState": "complete"}
] """

    default_val = """
     [{"resources": {"dut1": "any_ts", "vcs": "registrar", "dut": "any_ts"}},
      {"action": "create_conference", "serverName": "dut"},
      {"action": "create_conference", "serverName": "dut1"},
      {"action": "participant_create", "serverName": "dut1", "cascadeRole": "cascadeSlave" },
      {"action": "participant_dial", "serverName": "dut", "cascadeRole": "cascadeSlave", "remoteServerName": "dut1" },
      {"action": "verify_call_count", "serverName": "dut", "scenario": "call should have failed after wrong cascade roles", "expectedCount": "0"},
      {"action": "check_eventlog", "serverName": "dut", "severity": "Error", "message": "mismatch"}]
     """
    jsonText = forms.CharField(label="", widget=forms.Textarea(attrs={"class": "txtarea", "id":"jsonText", "placeholder": "Enter your json script here"}), initial=default_val)
    pythonScript = forms.CharField(label="", widget=forms.Textarea(attrs={ "class": "txtarea", "id":"pythonScript", "readonly": "readonly", "rows": "1", "cols": ""}), initial="python script here")
    testLog = forms.CharField(label="", widget=forms.Textarea(attrs={ "class": "txtarea", "id":"testLog", "readonly": "readonly", "rows": "1", "cols": ""}), initial="logs here")
    