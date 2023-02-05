# https://fapesp.br/12042/tabela-de-diarias-de-viagem

# Portaria 35:
# IV - Diária com pernoite: valor concedido por dia, destinado a custear as despesas com alimentação,
# hospedagem e locomoção urbana, quando há deslocamento do município sede com a realização de pousada;
# V - Diária sem pernoite: valor concedido por dia, destinado a custear as despesas com alimentação e
# locomoção urbana, quando há deslocamento do município sede sem a realização de pousada;
# VI - Diária para refeições: valor concedido por dia, destinado a custear as despesas com alimentação,
# para participação em evento no mesmo município sede, mas fora da Instituição Sede;

# X - Município sede:
# a) para os outorgados: município em que se localiza a Instituição Sede do projeto, indicada no processo; e
# b) para membros de equipe não vinculados à Instituição que sedia o projeto: município em que se localiza a Instituição de vínculo do respectivo membro de equipe;


# § 3º Nos casos em que, devido aos horários da programação oficial de um ou mais eventos,
# for necessário chegar no dia anterior ao seu início e retornar no dia seguinte ao seu término,
#  poderá ser considerada uma diária adicional aos dias dos eventos, respeitados os limites definidos nos Arts. 5º e 6º.

# § 4º Para fins de manutenção mensal, na contagem da fração de mês, será sempre considerado mês comercial de trinta dias.

# § 5º A adequação dos gastos com diárias e manutenção mensal será analisada pela FAPESP com base nas justificativas
# e documentos comprobatórios enviados nos Relatórios Científicos e Prestações de Contas,
# a serem apresentados conforme normas específicas,
#  nas datas estabelecidas no Termo de Outorga e Aceitação de Auxílios e Bolsas.

# § 6º O pagamento de diárias e manutenção mensal no país para pesquisadores que não sejam
# membros de equipe aprovados pela FAPESP poderá ser realizado nas seguintes hipóteses:

from money.money import Money
from money.currency import Currency
from datetime import datetime
from pathlib import Path
from docx import Document
from python_docx_replace import docx_replace
from num2words import num2words
from dados import my_dict
import locale

HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()
RESULTS = HERE.parent.joinpath("results").resolve()
import json

locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")


def main():
    international_values_dict = json.loads(
        RESULTS.joinpath("fapesp_international_values.json").read_text()
    )

    international_values_dict_computable = {}

    for country, country_data in international_values_dict.items():
        international_values_dict_computable[country] = dict()

        for location, value in country_data.items():
            international_values_dict_computable[country][location] = Money(
                value.replace(",", "."), Currency.USD
            )

    levels_plus = (
        "pesquisador dirigente coordenador assessor conselheiro pós-doutorando".split()
    )
    levels_base = ["bolsista (menos pós-doutorado)"]

    current_level = "bolsista (menos pós-doutorado)"

    daily_values_national = {
        "Brasil (Pesquisadores, dirigentes, coordenadores, assessores, conselheiros e pós-doutorandos)": {
            "Com pernoite (em capitais de Estado, Angra dos Reis (RJ), Brasília (DF), Búzios (RJ) e Guarujá (SP)": Money(
                "555.00", Currency.BRL
            )
        },
        "Brasil (bolsistas menos pós-doutorandos)": {
            "Com pernoite": Money("255.00", Currency.BRL),
            "Sem pernoite": Money("170.00", Currency.BRL),
        },
    }

    arrival_date_time = datetime.fromisoformat("2023-04-23T00:15:00")
    departure_date_time = datetime.fromisoformat("2023-04-28T00:19:00")

    event_start_date_time = datetime.fromisoformat("2023-04-24T00:08:00")
    event_end_date_time = datetime.fromisoformat("2023-04-26T00:16:00")

    event_duration = event_end_date_time - event_start_date_time
    trip_time = departure_date_time - arrival_date_time

    arrival_advance = event_start_date_time.day - arrival_date_time.day
    departure_gap = departure_date_time.day - event_end_date_time.day

    country = "Itália"
    location = "Demais localidades"

    value_for_location = international_values_dict_computable[country][location]
    if (event_duration.seconds) > 0:
        print(f"Considerando que o evento terá {event_duration.days+1} dias;")
        print(f"E que você chegará {arrival_advance} dia(s) antes do evento;")
        print(f"E que sairá {departure_gap} dia(s) depois do evento;")

        print(f"Você tem direito a {event_duration.days+1} diárias do evento")
        total_daily_stipends = event_duration.days + 1
        if arrival_advance > 0 and departure_gap > 0:
            print(
                f"E mais uma diária por chegar antes do dia que começa e sair depois do dia que termina."
            )
            total_daily_stipends += 1

        print(
            f"O valor que você pode solicitar para a localidade escolhida é de {value_for_location*total_daily_stipends},"
            f" correspondendo a {total_daily_stipends} x {str(value_for_location)}."
        )

        doc = Document("modelo_6_template.docx")

        value_in_brl = "100,25"
        print(number_to_long_number("100,25"))

        my_dict["valor_em_reais"] = value_in_brl
        my_dict["valor_por_extenso"] = number_to_long_number(value_in_brl)
        my_dict["data_inicial"] = event_start_date_time.strftime("%d de %B de %Y")
        my_dict["data_final"] = event_end_date_time.strftime("%d de %B de %Y")
        my_dict[
            "adendo"
        ] = " e mais 1 diária devido à chegada em dia anterior e saída em dia posterior ao evento, conforme rege o §3º da Portaria 35 da FAPESP, "

        my_dict["nome_do_evento"] = "Natal Bioinformatics Forum"
        my_dict["local_do_evento"] = "Natal (RN)"
        my_dict["data_de_hoje"] = datetime.now().strftime("%d de %B de %Y")

        docx_replace(doc, **my_dict)

        doc.save(f"modelo_preenchido.docx")


def number_to_long_number(number_p):
    if number_p.find(",") != -1:
        number_p = number_p.split(",")
        number_p1 = int(number_p[0].replace(".", ""))
        number_p2 = int(number_p[1])
    else:
        number_p1 = int(number_p.replace(".", ""))
        number_p2 = 0

    if number_p1 == 1:
        aux1 = " real"
    else:
        aux1 = " reais"

    if number_p2 == 1:
        aux2 = " centavo"
    else:
        aux2 = " centavos"

    text1 = ""
    if number_p1 > 0:
        text1 = num2words(number_p1, lang="pt") + str(aux1)
    else:
        text1 = ""

    if number_p2 > 0:
        text2 = num2words(number_p2, lang="pt") + str(aux2)
    else:
        text2 = ""

    if number_p1 > 0 and number_p2 > 0:
        result = text1 + " e " + text2
    else:
        result = text1 + text2

    return result


if __name__ == "__main__":
    main()
