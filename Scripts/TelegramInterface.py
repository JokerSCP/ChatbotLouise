from TelegramManager import TelegramManager
from time import sleep

# Iniciando telegram
is_production = True
manager = TelegramManager(True)
while True:
    if is_production:
        try:
            print("Iniciando servico...")
            manager.start_api_manager()
            manager.start_text_manager()
            manager.start_telegram()
        except:
            print("Reiniciando...")
        sleep(5)
    else:
        print("Iniciando servico...")
        manager.start_api_manager()
        manager.start_text_manager()
        manager.start_telegram()

