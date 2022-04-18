from APIManager import APIManager

# Testando APIManager
manager = APIManager(True)
manager.get_token()
manager.get_apikey()
manager.get_chatbot_intention_bag_list()
manager.get_message_list()

print("Ok")



