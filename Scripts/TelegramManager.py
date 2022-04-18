import telebot
import json
import random
import pickle
import numpy as np
import os
from datetime import datetime
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from APIManager import APIManager
from ProcessingTextManager import ProcessingTextManager


class TelegramManager:
    def __init__(self, enable_verbose=False):
        with open('../Models/intentionBag.json', 'r') as openfile:
            self.intention_bag = json.load(openfile)
        self.words = pickle.load(open('../Models/words.pkl', 'rb'))
        self.classes = pickle.load(open('../Models/classes.pkl', 'rb'))
        self.model = load_model('../Models/louise.model')
        self.news_folder = '../Assets/News/'
        self.restaurant_menu_folder = '../Assets/RestaurantMenu'
        self.available_vacancies_folder = '../Assets/AvailableVacancies'
        self.network_dentist_folder = '../Assets/NetworkDentist'
        self.network_doctor_folder = '../Assets/NetworkDoctor'
        self.bus_information_folder = '../Assets/BusInformation'
        self.threshold = 0
        self.verbose = enable_verbose
        self.bot = None
        self.api_manager = None
        self.text_manager = None
        self.chat_state = {}
        self.need_authentication = True

    def get_chat_state(self, chat_id):
        chat = []
        if str(chat_id) in self.chat_state.keys():
            chat = self.chat_state[str(chat_id)]
        if len(chat) == 0:
            chat = ["", "", datetime.now(), 0, ""]
            self.chat_state[str(chat_id)] = chat
        return chat

    def set_chat_state(self, chat_id, intention_name, state):
        chat = []
        if str(chat_id) in self.chat_state.keys():
            aux = self.chat_state[str(chat_id)]
            chat = [intention_name, state, datetime.now(), aux[3], aux[4]]
            self.chat_state[str(chat_id)] = chat
        if len(chat) == 0:
            chat = [intention_name, state, datetime.now(), 0, ""]
            self.chat_state[str(chat_id)] = chat

    def bag_of_words(self, sentence):
        aux = self.text_manager.process_sentence(sentence)
        bag = [0] * len(self.words)
        for w in aux:
            for i, word in enumerate(self.words):
                if word == w:
                    bag[i] = 1
        if self.verbose:
            print("Resultado do BagOfWords: {0}".format(bag))
        return np.array(bag)

    def predict_class(self, sentence):
        bow = self.bag_of_words(sentence)
        result = self.model.predict(np.array([bow]))[0]
        result_list = [[i, r] for i, r in enumerate(result) if r > self.threshold]
        result_list.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in result_list:
            return_list.append({'intention': self.classes[r[0]], 'probability': str(r[1])})
        if self.verbose:
            print("Resultado original: {0}".format(result))
            print("Intencao de retorno rankeado: {0}".format(return_list))
        return return_list

    def find_response_in_list(self, intention_name, response_type):
        list_of_intents = self.intention_bag
        result = ""
        for i in list_of_intents:
            if i.get("classIntention") == intention_name:
                if response_type == "RESPONSE":
                    result = random.choice(i.get("responseList"))
                if response_type == "EXPLANATION":
                    result = random.choice(i.get("explanationResponseList"))
                if response_type == "ASSET":
                    result = random.choice(i.get("assetResponseList"))
                break
        return result

    def content_type_to_chatbot_message_type(self, message_type):
        aux = 0
        if message_type == "text":
            aux = 0
        if message_type == "photo":
            aux = 2
        if (message_type == "video_note") or (message_type == "video") or (message_type == "voice") or (message_type == "audio"):
            aux = 3
        if message_type == "location":
            aux = 4
        if message_type == "document":
            aux = 5
        return aux

    def add_assets(self, message):
        assets = []
        asset_types = ["photo", "video_note", "video", "voice", "audio", "document"]
        if message.content_type in asset_types:
            folder = os.path.join("../Assets/Chat" + str(message.chat.id))
            remote_folder = os.path.join("//srvfs01/dados/dados/Comum/TI/ChatbotAsset/Chat" + str(message.chat.id))
            if not(os.path.isdir(folder)):
                os.makedirs(folder)
            if not(os.path.isdir(remote_folder)):
                os.makedirs(remote_folder)
            asset = None
            # Fotos
            if message.content_type == "photo":
                file_size = 0
                file = None
                dw_file = None
                for i in message.photo:
                    if self.verbose:
                        print(i.file_id)
                    if file_size < i.file_size:
                        file = self.bot.get_file(i.file_id)
                        dw_file = self.bot.download_file(file.file_path)
                        file_size = i.file_size
                file_extension = "png"
                file_path = os.path.join(folder, file.file_unique_id + "." + file_extension)
                file_remote_path = os.path.join(remote_folder, file.file_unique_id + "." + file_extension)
                with open(file_path, 'wb') as new_file:
                    new_file.write(dw_file)
                with open(file_remote_path, 'wb') as new_file:
                    new_file.write(dw_file)
                build_folder_path = os.path.join(remote_folder.replace('/', '\\'), file.file_unique_id + "." + file_extension)
                asset = {"FileName": "Imagem." + file_extension,
                         "FileMimeType": "image/" + file_extension,
                         "FileExtension": file_extension,
                         "FilePath": build_folder_path}
            # Documentos
            if message.content_type == "document":
                i = message.document
                if self.verbose:
                    print(i.file_id)
                file = self.bot.get_file(i.file_id)
                dw_file = self.bot.download_file(file.file_path)
                file_path = os.path.join(folder, i.file_name)
                file_remote_path = os.path.join(remote_folder, i.file_name)
                with open(file_path, 'wb') as new_file:
                    new_file.write(dw_file)
                with open(file_remote_path, 'wb') as new_file:
                    new_file.write(dw_file)
                build_folder_path = os.path.join(remote_folder.replace('/', '\\'), i.file_name)
                file_name, file_extension = os.path.splitext(i.file_name)
                file_extension = file_extension.replace('.', '')
                asset = {"FileName": i.file_name,
                         "FileMimeType": i.mime_type,
                         "FileExtension": file_extension,
                         "FilePath": build_folder_path}
            # Video
            if message.content_type == "video":
                i = message.video
                if self.verbose:
                    print(i.file_id)
                file_extension = i.mime_type.replace("video/", "")
                file = self.bot.get_file(i.file_id)
                dw_file = self.bot.download_file(file.file_path)
                file_path = os.path.join(folder, i.file_unique_id + "." + file_extension)
                file_remote_path = os.path.join(remote_folder, i.file_unique_id + "." + file_extension)
                with open(file_path, 'wb') as new_file:
                    new_file.write(dw_file)
                with open(file_remote_path, 'wb') as new_file:
                    new_file.write(dw_file)
                build_folder_path = os.path.join(remote_folder.replace('/', '\\'), i.file_unique_id + "." + file_extension)
                asset = {"FileName": "Video" + "." + file_extension,
                         "FileMimeType": i.mime_type,
                         "FileExtension": file_extension,
                         "FilePath": build_folder_path}
            # Video gravado pelo próprio telegram no chat
            if message.content_type == "video_note":
                i = message.video_note
                if self.verbose:
                    print(i.file_id)
                file_extension = "mp4"
                file = self.bot.get_file(i.file_id)
                dw_file = self.bot.download_file(file.file_path)
                file_path = os.path.join(folder, i.file_unique_id + "." + file_extension)
                file_remote_path = os.path.join(remote_folder, i.file_unique_id + "." + file_extension)
                with open(file_path, 'wb') as new_file:
                    new_file.write(dw_file)
                with open(file_remote_path, 'wb') as new_file:
                    new_file.write(dw_file)
                build_folder_path = os.path.join(remote_folder.replace('/', '\\'), i.file_unique_id + "." + file_extension)
                asset = {"FileName": "Video." + file_extension,
                         "FileMimeType": "video/" + file_extension,
                         "FileExtension": file_extension,
                         "FilePath": build_folder_path}
            # Audio gravado pelo proprio telegram no chat
            if message.content_type == "voice":
                i = message.voice
                if self.verbose:
                    print(i.file_id)
                file_extension = i.mime_type.replace("audio/", "")
                file = self.bot.get_file(i.file_id)
                dw_file = self.bot.download_file(file.file_path)
                file_path = os.path.join(folder, i.file_unique_id + "." + file_extension)
                file_remote_path = os.path.join(remote_folder, i.file_unique_id + "." + file_extension)
                with open(file_path, 'wb') as new_file:
                    new_file.write(dw_file)
                with open(file_remote_path, 'wb') as new_file:
                    new_file.write(dw_file)
                build_folder_path = os.path.join(remote_folder.replace('/', '\\'), i.file_unique_id + "." + file_extension)
                asset = {"FileName": "Audio." + file_extension,
                         "FileMimeType": i.mime_type,
                         "FileExtension": file_extension,
                         "FilePath": build_folder_path}
            # Audio
            if message.content_type == "audio":
                i = message.audio
                if self.verbose:
                    print(i.file_id)
                file = self.bot.get_file(i.file_id)
                dw_file = self.bot.download_file(file.file_path)
                file_path = os.path.join(folder, i.file_name)
                file_remote_path = os.path.join(remote_folder, i.file_name)
                with open(file_path, 'wb') as new_file:
                    new_file.write(dw_file)
                with open(file_remote_path, 'wb') as new_file:
                    new_file.write(dw_file)
                build_folder_path = os.path.join(remote_folder.replace('/', '\\'), i.file_name)
                file_name, file_extension = os.path.splitext(i.file_name)
                file_extension = file_extension.replace('.', '')
                asset = {"FileName": i.file_name,
                         "FileMimeType": i.mime_type,
                         "FileExtension": file_extension,
                         "FilePath": build_folder_path}
            # Retorno
            if asset is not None:
                assets.append(asset)
        return assets

    def send_files_in_folder(self, folder, chat_id):
        objects = [os.path.join(folder, name) for name in os.listdir(folder)]
        files = [file for file in objects if os.path.isfile(file)]
        if len(files) == 0:
            self.bot.send_message(chat_id, "Nossa, me desculpe... Não encontrei as informações que pediu... Vou falar com o RH...")
        for file in files:
            doc = open(file, 'rb')
            self.bot.send_document(chat_id, doc)

    def do_simple_response(self, intention_name, chat_id, api_message):
        # Inicia salvando a mensagem do usuário
        self.api_manager.save_message_bag(api_message)
        # Rotina normal
        response_aux = self.find_response_in_list(intention_name, "RESPONSE")
        # Personalizar a saída de saudação
        current = datetime.now()
        hours = current.hour
        grt = ""
        grt_upper = ""
        if (hours >= 18) and (hours < 6):
            grt = "boa noite"
            grt_upper = "Boa noite"
        elif (hours >= 6) and (hours < 12):
            grt = "bom dia"
            grt_upper = "Bom dia"
        else:
            grt = "boa tarde"
            grt_upper = "Boa tarde"
        response_plus = response_aux.replace('[grt]', grt)
        response = response_plus.replace('[GRT]', grt_upper)
        # Enviar a resposta e os anexos
        self.bot.send_chat_action(chat_id, "typing")
        self.bot.send_message(chat_id, response)
        if intention_name == "AVAILABLE_VACANCIES":
            self.send_files_in_folder(self.available_vacancies_folder, chat_id)
        if intention_name == "NEWS":
            self.send_files_in_folder(self.news_folder, chat_id)
        if intention_name == "NETWORK_DOCTORS":
            self.send_files_in_folder(self.network_doctor_folder, chat_id)
        if intention_name == "NETWORK_DENTIST":
            self.send_files_in_folder(self.network_dentist_folder, chat_id)
        if intention_name == "RESTAURANT_MENU":
            self.send_files_in_folder(self.restaurant_menu_folder, chat_id)
        if intention_name == "BUS_INFORMATION":
            self.send_files_in_folder(self.bus_information_folder, chat_id)
        message = api_message
        message["MessageTransDate"] = str(datetime.today())
        message["MessageText"] = response
        message["MessagePart"] = 1
        message["Predict"] = 0
        self.api_manager.save_message_bag(message)
        self.set_chat_state(chat_id, "", "")

    def do_confirmation(self, intention_name, chat_id, api_message):
        # Inicia salvando a mensagem do usuário
        api_message["StartDemand"] = True
        self.api_manager.save_message_bag(api_message)
        # Rotina normal
        response = self.find_response_in_list(intention_name, "RESPONSE")
        self.bot.send_chat_action(chat_id, "typing")
        self.bot.send_message(chat_id, response)
        message = api_message;
        message["MessageTransDate"] = str(datetime.today())
        message["MessageText"] = response
        message["MessagePart"] = 1
        message["StartDemand"] = False
        self.api_manager.save_message_bag(message)
        self.set_chat_state(chat_id, intention_name, "CONFIRMATION")

    def do_protocol(self, chat_id, chat_state, api_message):
        # Inicia salvando a mensagem do usuário
        api_message["IntentionCode"] = chat_state[0]
        api_message["Predict"] = 0
        self.api_manager.save_message_bag(api_message)
        # Rotina normal
        action_describe = "X"
        protocol = {"ChatbotCode": 1,
                    "TalkExternalCode": str(chat_id),
                    "IntentionCode": chat_state[0],
                    "UserFeedback": 0,
                    "ActionDescribe": action_describe,
                    "ProtocolCode": ""}
        protocol = self.api_manager.save_demand_bag(protocol)
        # Salva a mensagem
        response = "Protocolo {} gerado com sucesso!".format(protocol["protocolCode"])
        self.set_chat_state(chat_id, "", "")
        self.bot.send_chat_action(chat_id, "typing")
        self.bot.send_message(chat_id, response)
        message = api_message
        message["MessageTransDate"] = str(datetime.today())
        message["MessageText"] = response
        message["MessagePart"] = 1
        message["ProtocolCode"] = protocol["protocolCode"]
        self.api_manager.save_message_bag(message)

    def do_explanation(self, chat_id, chat_state, api_message):
        # Inicia salvando a mensagem do usuário
        api_message["IntentionCode"] = chat_state[0]
        api_message["Predict"] = 0
        self.api_manager.save_message_bag(api_message)
        # Rotina normal
        response = self.find_response_in_list(chat_state[0], "EXPLANATION")
        self.set_chat_state(chat_id, chat_state[0], "EXPLANATION")
        self.bot.send_chat_action(chat_id, "typing")
        self.bot.send_message(chat_id, response)
        message = api_message
        message["MessageTransDate"] = str(datetime.today())
        message["MessageText"] = response
        message["MessagePart"] = 1
        message["IntentionCode"] = chat_state[0]
        self.api_manager.save_message_bag(message)

    def do_asset_in_protocol(self, chat_id, chat_state, api_message):
        # Inicia salvando a mensagem do usuário
        api_message["IntentionCode"] = chat_state[0]
        api_message["Predict"] = 0
        self.api_manager.save_message_bag(api_message)
        # Rotina normal
        response = self.find_response_in_list(chat_state[0], "ASSET")
        self.set_chat_state(chat_id, chat_state[0], "ASSET")
        self.bot.send_chat_action(chat_id, "typing")
        self.bot.send_message(chat_id, response)
        message = api_message
        message["MessageTransDate"] = str(datetime.today())
        message["MessageText"] = response
        message["MessagePart"] = 1
        self.api_manager.save_message_bag(message)

    def do_positive_confirmation(self, chat_id, chat_state, api_message):
        # Gera protocolo depois da confirmação
        protocol = ["PHARMACY_CARD_COPY", "FOOD_CARD_COPY", "IRPF_VOUCHER", "NEW_BADGE", "FINANCING_MARGIN", \
        "OPTICAL_AUTHORIZATION", "DENTIST_CARD_COPY", "HEALTH_PLAN_CARD_COPY"]
        if chat_state[0] in protocol:
            self.do_protocol(chat_id, chat_state, api_message)
        # Necessita de explicação depois da confirmação
        explanation = ["HEALTH_PLAN_HANDLING", "PAYROLL", "DENTIST_PLAN_HANDLING", "LIFE_INSURANCE_HANDLING"]
        if chat_state[0] in explanation:
            self.do_explanation(chat_id, chat_state, api_message)
        # Anexa um arquivo
        asset_in_protocol = ["ADDRESS_CHANGE", "MEDICAL_CERTIFICATE", "SEND_CURRICULUM"]
        if chat_state[0] in asset_in_protocol:
            self.do_asset_in_protocol(chat_id, chat_state, api_message)

    def do_negative_confirmation(self, chat_id, api_message):
        # Inicia salvando a mensagem do usuário
        self.api_manager.save_message_bag(api_message)
        # Rotina normal
        response = "Cancelando a operação... Se precisar de alguma coisa, é só chamar!"
        self.bot.send_chat_action(chat_id, "typing")
        self.bot.send_message(chat_id, response)
        message = api_message
        message["MessageTransDate"] = str(datetime.today())
        message["MessageText"] = response
        message["MessagePart"] = 1
        self.api_manager.save_message_bag(message)
        self.set_chat_state(chat_id, "", "")

    def do_start_tag(self, chat_id, api_message):
        # Inicia salvando a mensagem do usuário
        api_message["IntentionCode"] = "X"
        self.api_manager.save_message_bag(api_message)
        # Rotina normal
        if self.need_authentication:
            self.do_authentication(chat_id, api_message)
        response = "Oi, eu sou a Louise, se precisar de alguma coisa, é só chamar!"
        self.set_chat_state(chat_id, "", "")
        self.bot.send_chat_action(chat_id, "typing")
        self.bot.send_message(chat_id, response)
        message = api_message
        message["MessageTransDate"] = str(datetime.today())
        message["MessageText"] = response
        message["MessagePart"] = 1
        self.api_manager.save_message_bag(message)

    def do_authentication(self, chat_id, api_message):
        # Inicia salvando a mensagem do usuário
        api_message["IntentionCode"] = "X"
        self.api_manager.save_message_bag(api_message)
        # Rotina normal
        response = "Olá {}, eu sou Louise... Para que eu possa atendê-lo eu preciso confirmar suas credenciais. Por favor digite seu CPF:"
        response = response.format(api_message["UserExternalAlias"])
        self.set_chat_state(chat_id, "", "AUTHENTICATION")
        self.bot.send_chat_action(chat_id, "typing")
        self.bot.send_message(chat_id, response)
        message = api_message
        message["MessageTransDate"] = str(datetime.today())
        message["MessageText"] = response
        message["MessagePart"] = 1
        self.api_manager.save_message_bag(message)

    def do_confirm_cpf(self, chat_id, api_message):
        # Inicia salvando a mensagem do usuário
        api_message["IntentionCode"] = "X"
        self.api_manager.save_message_bag(api_message)
        # Rotina normal
        aux = self.api_manager.authenticated_talk(chat_id, api_message["MessageText"])
        if aux is not None:
            response = "Seja bem vindo " + aux["userName"] + "! Em que posso ajudá-lo?"
            chat = ["", "", datetime.now(), aux["userCode"], aux["userName"]]
            self.chat_state[str(chat_id)] = chat
        else:
            response = "Não foi possível confirmar suas credenciais!"
            self.set_chat_state(chat_id, "", "")
        self.bot.send_chat_action(chat_id, "typing")
        self.bot.send_message(chat_id, response)
        message = api_message
        message["MessageTransDate"] = str(datetime.today())
        message["MessageText"] = response
        message["MessagePart"] = 1
        self.api_manager.save_message_bag(message)

    def do_machine_learning(self, chat_id, api_message):
        # Inicia salvando a mensagem do usuário
        self.api_manager.save_message_bag(api_message)
        # Rotina normal
        response = "Eu sou nova ainda, estou aprendendo algumas coisas e não entendi seu pedido. Vou pedir ao pessoal "
        response = response + "do RH que me explique e na próxima vez que precisar, vou conseguir ajudá-lo!"
        self.set_chat_state(chat_id, "", "")
        self.bot.send_chat_action(chat_id, "typing")
        self.bot.send_message(chat_id, response)
        message = api_message
        message["MessageTransDate"] = str(datetime.today())
        message["MessageText"] = response
        message["MessagePart"] = 1
        self.api_manager.save_message_bag(message)

    def process_message(self, messages):
        for m in messages:
            # Tratamento com a mensagem recebida
            print("Mensagem recebida: {}".format(m))
            chat_id = m.chat.id
            from_user_id = m.from_user.id
            from_user_alias = ""
            if m.from_user.first_name is not None:
                from_user_alias = m.from_user.first_name
            if m.from_user.last_name is not None:
                from_user_alias = from_user_alias + " " + m.from_user.last_name
            message_id = m.message_id
            text = m.text
            if text is None:
                text = "Arquivo"
            message_type = self.content_type_to_chatbot_message_type(m.content_type)
            assets = self.add_assets(m)
            chat_state = self.get_chat_state(chat_id)
            if self.verbose:
                print("Estado do chat: {}".format(chat_state))
            message = {"ChatbotCode": 1,
                       "TalkExternalCode": str(chat_id),
                       "UserExternalCode": str(from_user_id),
                       "UserExternalAlias": from_user_alias,
                       "MessageExternalId": str(message_id),
                       "MessageTransDate": str(datetime.today()),
                       "MessageType": message_type,
                       "MessageText": text,
                       "MessagePart": 0,
                       "AssetList": assets,
                       "IntentionCode": chat_state[0],
                       "StartDemand": False,
                       "ProtocolCode": "",
                       "Predict": 0
                       }
            if self.verbose:
                print("Mensagem enviada para API: {}".format(message))

            # Para salvar anexos, não há predição aqui nesse ponto, o intention é o estado do chat
            if m.content_type != "text":
                self.api_manager.save_message_bag(message)

            # Vai haver uma tentativa seguir o estado do chat, caso contrário haverá predição
            if m.content_type == "text":
                # Condição de autenticação
                if chat_state[3] == 0:
                    if chat_state[1] == "":
                        self.do_authentication(chat_id, message)
                        return
                    if chat_state[1] == "AUTHENTICATION":
                        self.do_confirm_cpf(chat_id, message)
                        return
                # Condição de Start
                if text.lower() == "/start":
                    self.do_start_tag(chat_id, message)
                    return
                # Etapa de explicação
                explanation = ["HEALTH_PLAN_HANDLING", "PAYROLL", "DENTIST_PLAN_HANDLING", "LIFE_INSURANCE_HANDLING"]
                if (chat_state[1] == "EXPLANATION") and (chat_state[0] in explanation):
                    self.do_asset_in_protocol(chat_id, chat_state, message)
                    return
                # Etapa de anexar arquivos
                asset = ["HEALTH_PLAN_HANDLING", "PAYROLL", "DENTIST_PLAN_HANDLING", "LIFE_INSURANCE_HANDLING", "ADDRESS_CHANGE", \
                "MEDICAL_CERTIFICATE", "SEND_CURRICULUM", "HEALTH_PLAN_HANDLING", "PAYROLL", "DENTIST_PLAN_HANDLING", "LIFE_INSURANCE_HANDLING"]
                if (chat_state[1] == "ASSET")  and (chat_state[0] in asset) and (text.lower() == "fim"):
                    self.do_protocol(chat_id, chat_state, message)
                    return
                # Encontra intenção
                intention = self.predict_class(text)
                # Se não encontrar a intenção marca mensagem para aprender
                if len(intention) == 0:
                    self.do_machine_learning(chat_id, message)
                    return
                intention_name = intention[0].get("intention")
                message["Predict"] = intention[0].get("probability")
                message["IntentionCode"] = intention_name
                if float(intention[0].get("probability")) <= 0.7:
                    self.do_machine_learning(chat_id, message)
                    return
                # Houve confirmação positiva
                if (chat_state[1] == "CONFIRMATION") and (intention_name == "POSITIVE_RESPONSE"):
                    self.do_positive_confirmation(chat_id, chat_state, message)
                    return
                # Houve confirmação negativa
                if (chat_state[1] == "CONFIRMATION") and (intention_name == "NEGATIVE_RESPONSE"):
                    self.do_negative_confirmation(chat_id, message)
                    return
                # Resposta simples
                simple_response = ["SALARY_INCREASE", "AVAILABLE_VACANCIES", "JOKE", "NEWS", "CTPS_HANDLING", "NETWORK_DOCTORS", \
                "NETWORK_DENTIST", "INTERVIEW", "RESTAURANT_MENU", "LACK_OF_EDUCATION", "GREETINGS", "VACATION", "BUS_INFORMATION"]
                if intention_name in simple_response:
                    self.do_simple_response(intention_name, chat_id, message)
                    return
                # Precisa de confirmação
                confirmation_and_protocol = ["ADDRESS_CHANGE", "MEDICAL_CERTIFICATE", "SEND_CURRICULUM", "HEALTH_PLAN_HANDLING", "PAYROLL", \
                "DENTIST_PLAN_HANDLING", "LIFE_INSURANCE_HANDLING", "FOOD_CARD_COPY", "IRPF_VOUCHER", "NEW_BADGE", "FINANCING_MARGIN", \
                "OPTICAL_AUTHORIZATION", "DENTIST_CARD_COPY", "HEALTH_PLAN_CARD_COPY", "PHARMACY_CARD_COPY"]
                if intention_name in confirmation_and_protocol:
                    self.do_confirmation(intention_name, chat_id, message)
                    return
                # Se nenhuma etapa do fluxo se apropriar da mensagem a etapa final grava a mensagem com intuito de aprendizado
                self.do_machine_learning(chat_id, message)
                return

    def start_api_manager(self):
        self.api_manager = APIManager(self.verbose)
        self.api_manager.get_token()
        self.api_manager.get_apikey()
        aux = self.api_manager.get_chatbot_talk_list()
        for item in aux:
            chat = ["", "", datetime.now(), item["userCode"], item["userName"]]
            self.chat_state[item["talkExternalId"]] = chat

    def start_text_manager(self):
        self.text_manager = ProcessingTextManager(self.verbose)

    def start_telegram(self):
        self.bot = telebot.TeleBot(self.api_manager.api_key)
        self.bot.set_update_listener(self.process_message)
        print("Pooling iniciado...")
        self.bot.polling()
