import requests
import json
import datetime
from time import sleep


class APIManager:
    def __init__(self, enable_verbose=False):
        # URLs
        self.url_endpoint = 'https://gfintegration.usinaferrari.com.br/'
        self.url_resource_token = self.url_endpoint + 'api/v1/token/sign'
        self.url_resource_post_message_bag = self.url_endpoint + 'api/v1/chatbot/message/bag'
        self.url_resource_chatbot = self.url_endpoint + 'api/v1/chatbot/byid'
        self.url_resource_chatbot_intention_bag_list = self.url_endpoint + 'api/v1/chatbot/intention/bag/bychatbotid'
        self.url_resource_post_demand_bag = self.url_endpoint + 'api/v1/chatbot/demand/bag'
        self.url_resource_talk_list = self.url_endpoint + 'api/v1/chatbot/talk/bychatbotid'
        self.url_resource_authenticated_talk = self.url_endpoint + 'api/v1/chatbot/talk/authenticated'
        self.url_resource_message_list = self.url_endpoint + 'api/v1/chatbot/message/list/byhuman'
        self.verbose = enable_verbose
        self.chatbotId = 1
        self.token = "X"
        self.token_due = datetime.datetime.now() - datetime.timedelta(days=1)
        self.retry = 3
        self.api_key = "X"
        self.login_json = {"UserId": "integracaod365gfapi",
                          "Password": "3IQ69&hJ+CMVtu*E26sZLA1#+VBkqY",
                          "DateTimeSource": "2020-09-10T11:20:00",
                          "DomainName": "EXTERNO",
                          "ProductId": "GFINTEGRATION",
                          "Method": 0,
                          "LoginKeyList": []}

    def get_token(self):
        check = datetime.datetime.now()
        if check > self.token_due:
            self.token = "X"
        if self.token == "X":
            counter = 1
            while (counter <= self.retry) & (self.token == "X"):
                try:
                    if self.verbose:
                        print("Iniciando GetToken, tentativa {0} : {1}".format(counter, self.url_resource_token));
                    header = {'Content-Type': 'application/json; charset=utf-8'}
                    r = requests.post(self.url_resource_token, data=json.dumps(self.login_json), headers=header)
                    js = r.json()
                    if js["isSucess"]:
                        self.token = js["objectResult"]
                        self.token_due = datetime.datetime.now() + datetime.timedelta(minutes=1410)
                except:
                    print("Erro em GetToken!")
                    sleep(1)
                counter = counter + 1
            if self.verbose and (self.token != "X"):
                print("GetToken coletado: {0}".format(self.token))
        return self.token

    def get_apikey(self):
        if self.api_key == "X":
            tkn = self.get_token()
            if tkn != "X":
                counter = 1
                while (counter <= self.retry) & (self.api_key == "X"):
                    try:
                        if self.verbose:
                            print("Iniciando GetAPIKey, tentativa {0}: {1}".format(counter, self.url_resource_chatbot))
                        header = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + tkn}
                        params = {"id": self.chatbotId}
                        r = requests.get(self.url_resource_chatbot, headers=header, params=params)
                        js = r.json()
                        if js["isSucess"]:
                            self.api_key = js["objectResult"]["apiKey"]
                    except:
                        print("Erro em GetAPIKey!")
                        sleep(1)
                    counter = counter + 1
            if self.verbose and (self.api_key != "X"):
                print("GetAPIKey coletado: {0}".format(self.api_key))
        return self.api_key

    def get_chatbot_intention_bag_list(self):
        tkn = self.get_token()
        if tkn != "X":
            counter = 1
            aux = "X"
            while (counter <= self.retry) & (aux == "X"):
                try:
                    if self.verbose:
                        print("Iniciando GetChatbotIntentionBagList, tentativa {0}: {1}".format(counter, self.url_resource_chatbot_intention_bag_list))
                    header = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + tkn}
                    params = {"id": self.chatbotId}
                    r = requests.get(self.url_resource_chatbot_intention_bag_list, headers=header, params=params)
                    js = r.json()
                    if js["isSucess"]:
                        aux = js["objectResult"]
                except:
                    print("Erro em GetChatbotIntentionBagList!")
                    sleep(1)
                counter = counter + 1
        if self.verbose and (aux != "X"):
            print("GetChatbotIntentionBagList coletado: {0}".format(aux))
        return aux

    def get_message_list(self):
        tkn = self.get_token()
        if tkn != "X":
            counter = 1
            aux = "X"
            while (counter <= self.retry) & (aux == "X"):
                try:
                    if self.verbose:
                        print("Iniciando GetMessageList, tentativa {0}: {1}".format(counter, self.url_resource_message_list))
                    header = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + tkn}
                    params = {"id": self.chatbotId}
                    r = requests.get(self.url_resource_message_list, headers=header, params=params)
                    js = r.json()
                    if js["isSucess"]:
                        aux = js["objectResult"]
                except:
                    print("Erro em GetMessageList!")
                    sleep(1)
                counter = counter + 1
        if self.verbose and (aux != "X"):
            print("GetMessageList coletado: {0}".format(aux))
        return aux

    def save_message_bag(self, bag):
        tkn = self.get_token()
        if tkn != "X":
            counter = 1
            aux = "X"
            while (counter <= self.retry) & (aux == "X"):
                try:
                    if self.verbose:
                        print("Iniciando SaveMessageBag, tentativa {0}: {1}".format(counter, self.url_resource_post_message_bag));
                    header = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + tkn}
                    r = requests.post(self.url_resource_post_message_bag, data=json.dumps(bag), headers=header)
                    js = r.json()
                    if js["isSucess"]:
                        aux = "Ok"
                except:
                    print("Erro em SaveMessageBag!")
                    sleep(1)
                counter = counter + 1
        if self.verbose and (aux != "X"):
            print("SaveMessageBag coletado: {0}".format(r.content))

    def save_demand_bag(self, bag):
        tkn = self.get_token()
        if tkn != "X":
            counter = 1
            aux = "X"
            while (counter <= self.retry) & (aux == "X"):
                try:
                    if self.verbose:
                        print("Iniciando SaveDemandBag, tentativa {0}: {1}".format(counter, self.url_resource_post_demand_bag));
                    header = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + tkn}
                    r = requests.post(self.url_resource_post_demand_bag, data=json.dumps(bag), headers=header)
                    js = r.json()
                    if js["isSucess"]:
                        aux = js["objectResult"]
                except:
                    print("Erro em SaveDemandBag!")
                    sleep(1)
                counter = counter + 1
        if self.verbose and (aux != "X"):
            print("SaveDemandBag coletado: {0}".format(r.content))
        return aux

    def get_chatbot_talk_list(self):
        tkn = self.get_token()
        if tkn != "X":
            counter = 1
            aux = "X"
            while (counter <= self.retry) & (aux == "X"):
                try:
                    if self.verbose:
                        print("Iniciando GetChatbotTalkList, tentativa {0}: {1}".format(counter, self.url_resource_talk_list))
                    header = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + tkn}
                    params = {"chatbotId": self.chatbotId}
                    r = requests.get(self.url_resource_talk_list, headers=header, params=params)
                    js = r.json()
                    if js["isSucess"]:
                        aux = js["objectResult"]
                except:
                    print("Erro em GetChatbotTalkList!")
                    sleep(1)
                counter = counter + 1
        if self.verbose and (aux != "X"):
            print("GetChatbotTalkList coletado: {0}".format(aux))
        return aux

    def authenticated_talk(self, talk_external_id, cpf):
        tkn = self.get_token()
        if tkn != "X":
            counter = 1
            aux = "X"
            while (counter <= self.retry) & (aux == "X"):
                try:
                    if self.verbose:
                        print("Iniciando AuthenticatedTalk: {0}".format(self.url_resource_authenticated_talk))
                    header = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + tkn}
                    params = {"talkExternalId": talk_external_id, "cpf": cpf}
                    r = requests.get(self.url_resource_authenticated_talk, headers=header, params=params)
                    js = r.json()
                    if js["isSucess"]:
                        aux = js["objectResult"]
                except:
                    print("Erro em AuthenticatedTalk!")
                    sleep(1)
                counter = counter + 1
        if self.verbose and (aux != "X"):
            print("AuthenticatedTalk coletado: {0}".format(aux))
        return aux
