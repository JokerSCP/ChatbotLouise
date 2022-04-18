from ProcessingTextManager import ProcessingTextManager

manager = ProcessingTextManager(True)
#aux = manager.process_sentence("Louise, eu preciso adicionar meu pai como dependente do plano de saúde, pode ser dia 20?")
aux = manager.process_sentence("Qual é o horário do busão?")
print(aux)