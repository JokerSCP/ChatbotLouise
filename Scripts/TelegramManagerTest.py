from TelegramManager import TelegramManager

# Testando APIManager
manager = TelegramManager(False)
manager.start_api_manager()
manager.start_text_manager()

while True:
    print("Vamos lá, diga alguma coisa: ")
    message = input()
    intention = manager.predict_class(message)
    print(intention)

print("Ok")
