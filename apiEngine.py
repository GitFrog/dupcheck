from datetime import datetime
import json
import requests

class api:

    def __init__(self):
        #self.getUrl = "https://intra.cognosbi.css.gov.on.ca/BIPDServices/api/email/1"
        self.adminEmails = "lee.hulsesmith@ontario.ca"
        self.url = "https://intra.cognosbi.css.gov.on.ca/BIPDServices/api/email"
        self.header = {"Accept": "application/json",
                                "Content-Type": "application/json;charset=UTF-8"}
        self.data = {"body": "",
                            "recipient": "",
                            "module": "accerta",
                            "priority": "1",
                            "created_dt": "",
                            "sent_dt": "",
                            "active": True,
                            "status": "0"}

    def get(self):
        response = requests.get(self.getUrl, headers=self.header)
        print(response.content)

    def post(self, msg, group):
        dte = datetime.today().strftime('%Y-%m-%d')
        self.data["recipient"] = self.getEmailRecipients(group)
        self.data["body"] = msg
        self.data["created_dt"] = dte
        self.data["sent_dt"] = dte
        response = requests.post(self.url, headers=self.header, data=json.dumps(self.data))

    def getEmailRecipients(self, group):
        if group == "me":
            return "lee.hulsesmith@ontario.ca"
        else:
            #s = "lee.hulsesmith@ontario.ca"
            s = "lee.hulsesmith@ontario.ca;MCCSS.L.OACIS.IIO.Monitor@msgov.gov.on.ca;Sunil.Arokiaswamy@ontario.ca;Stephen.Brooks2@ontario.ca"
            return s
