from TelegramManager import TelegramManager
import numpy as np


# Testando APIManager
manager = TelegramManager(False)
manager.start_api_manager()
manager.start_text_manager()

# Base de teste
train_test_list = []
train_test_list.append(["", 0, "SALARY_INCREASE", "Estou passando dificuldades, preciso que aumentem meu salário"])
train_test_list.append(["", 0, "AVAILABLE_VACANCIES", "Quero trocar de setor, quero me candidatar a uma vaga"])
train_test_list.append(["", 0, "BUS_INFORMATION", "Acordei tarde, preciso saber se o ônibus vai passar aqui"])
train_test_list.append(["", 0, "JOKE", "Me faça dar risada!"])
train_test_list.append(["", 0, "PHARMACY_CARD_COPY", "Eu perdi meu cartão da farmácia!"])
train_test_list.append(["", 0, "FOOD_CARD_COPY", "Eu perdi meu cartão de alimentação, o que faco?"])
train_test_list.append(["", 0, "IRPF_VOUCHER", "Preciso declarar meu imposto de renda, preciso do papel"])
train_test_list.append(["", 0, "NEW_BADGE", "Perdi o cartão da batida do cracha"])
train_test_list.append(["", 0, "HEALTH_PLAN_HANDLING", "Preciso colocar meu neto no plano de saúde"])
train_test_list.append(["", 0, "NEWS", "Tem alguma coisa nova?"])
train_test_list.append(["", 0, "ADDRESS_CHANGE", "Troquei de cidade, preciso atualizar o cadastro"])
train_test_list.append(["", 0, "MEDICAL_CERTIFICATE", "Cortei a mão, preciso entregar atestado!"])
train_test_list.append(["", 0, "FINANCING_MARGIN", "Estou apertado, preciso de consignado"])
train_test_list.append(["", 0, "OPTICAL_AUTHORIZATION", "Meu óculos antigo quebrou, preciso fazer novo óculos"])
train_test_list.append(["", 0, "SEND_CURRICULUM", "Meu amigo Adriano quer enviar um curriculo"])
train_test_list.append(["", 0, "CTPS_HANDLING", "Preciso levar a carteira atualizada na CDHU"])
train_test_list.append(["", 0, "NETWORK_DOCTORS", "Preciso da lista dos médicos da hapivida"])
train_test_list.append(["", 0, "NETWORK_DENTIST", "Preciso da lista de dentistas da unimed"])
train_test_list.append(["", 0, "INTERVIEW", "Como faço para fazer uma entrevista de emprego"])
train_test_list.append(["", 0, "DENTIST_CARD_COPY", "Perdi meu cartão do plano odontológico"])
train_test_list.append(["", 0, "HEALTH_PLAN_CARD_COPY", "Perdi meu cartão do plano de saúde"])
train_test_list.append(["", 0, "VACATION", "Quero vender minhas férias"])
train_test_list.append(["", 0, "PAYROLL", "Meu adiantamento não caiu na conta"])
train_test_list.append(["", 0, "DENTIST_PLAN_HANDLING", "Quero saber se o plano de dentista cobre clareamento"])
train_test_list.append(["", 0, "LIFE_INSURANCE_HANDLING", "Quero aumentar o prêmio do seguro"])
train_test_list.append(["", 0, "RESTAURANT_MENU", "O que há para comer no restaurante hoje?"])
train_test_list.append(["", 0, "LACK_OF_EDUCATION", "Vai pro inferno louise!"])
train_test_list.append(["", 0, "GREETINGS", "Salve, bom dia"])
train_test_list.append(["", 0, "POSITIVE_RESPONSE", "Positivo e operante"])
train_test_list.append(["", 0, "NEGATIVE_RESPONSE", "Negativo"])

# Predição
for test in train_test_list:
    intention = manager.predict_class(test[3])
    test[0] = intention[0]["intention"]
    test[1] = intention[0]["probability"]

# Calculando acurácia
hit_list = []
probability_sum = 0
for item in train_test_list:
    if (item[0] == item[2]):
        hit_list.append(item)
        probability_sum = probability_sum + float(item[1])
average_probability = probability_sum / len(hit_list)

error_list = []
for item in train_test_list:
    if (item[0] != item[2]):
        error_list.append(item)

# Resultado
print("Acertos {}".format(len(hit_list)))
print("Total {}".format(len(train_test_list)))
print("Acurácia {}".format(len(hit_list) / len(train_test_list)))
print("Média da probabilidade da predição {}".format(average_probability))
print("Erros: ")
for item in error_list:
    print(item)

print("Ok")
