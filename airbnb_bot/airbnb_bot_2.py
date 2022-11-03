import re # regex
import sqlite3 as sql # für den datensatz
from os.path import isfile # überprüft ob eine datei vorhanden ist


location_regex = [
    # first entry in every tuple is a regex for matching user inputs
    # second entry in every tuple is a possible value
    #   for the key neighbourhood_group in our sql file
    (r'(charlottenburg)|(wilmersdorf)','Charlottenburg-Wilm.'),
    (r'(friedrichshain)|(kreuzberg)', 'Friedrichshain-Kreuzberg'),
    (r'lichtenberg', 'Lichtenberg'),
    (r'(marzahn)|(Hellersdorf)', 'Marzahn - Hellersdorf'),
    (r'mitte', 'Mitte'),
    (r'neukölln', 'Neukölln'),
    (r'pankow', 'Pankow'),
    (r'reinickendorf', 'Reinickendorf'),
    (r'spandau', 'Spandau'),
    (r'(steglitz)|(zehlendorf)', 'Steglitz - Zehlendorf'),
    (r'(tempelhof)|(schöneberg)', 'Tempelhof - Schöneberg'),
    (r'(treptow)|(köpenick)', 'Treptow - Köpenick')
]


def get_location_from_input(sentence, regex_list=location_regex):
    """
    get valid location names from user input using RegEx
    """
    # iterate through regular expressions and associated values in regex_list
    for regex, value in regex_list:
        match = re.search(regex, sentence)
        if match:
            # if a regex matches the input: return the corresponding value
            return value
    # return None if no regular expression matches the input
    return None

def get_max_money_from_input(sentence):
    number = int(sentence)
    return number

def weiter_fragen(results,top_n):
    sentence2 = input('\nMöchtest du 10 weitere Ergebnisse sehen?\n')
    sentence2 = sentence2.lower()

    if sentence2 == 'ja': # mehr antwortmöglichkeiten anbieten?
        print('Alles klar, hier sind 10 weitere Ergebnisse:\n'.format(top_n))
        for r in results[10:20]:
            answer = '"{}", {}. Das Apartment kostet {}€.'.format(r[0], r[1], r[2])
            # look at the columns list to see what r[0], r[1], r[2] are referring to! r[0] = name / r[1] = neighborhood / r[2] = price
            print(answer)
    else:
        print('Dann halt nicht')

        return


def query_sql(key, value, columns, sql_file):
    """
    Query a sqlite file for entries where "key" has the value "value".
    Return the values corresponding to columns as a list.
    """

    # set up sqlite connection
    conn = sql.connect(sql_file)
    c = conn.cursor()


    # prepare query string
    query_template = 'SELECT {columns} FROM listings WHERE {key} = "{value}"' #AND ...  # template um daten aus der Datei zu bekommen
    columns_string = ', '.join(columns)  # e.g. [location, price] -> 'location, price'
    # replace the curly brackets in query_template with the corresponding info
    query = query_template.format(columns=columns_string, key=key, value=value)

    
    # execute query
    r = c.execute(query)
    # get results as list
    results = r.fetchall()

    # close connection
    conn.close()

    return results

# def price_sql(columns,sql_file):
#     conn = sql.connect(sql_file)
#     c = conn.cursor()

#     q_template = 'SELECT * FROM listing WHERE price > 100'
#     columns_string = ', '.join(columns)
#     query = q_template.format(columns=columns_string)

#     r = c.execute(query)
#     results = r.fetchall()

#     conn.close()

#     return results


def airbnb_bot(sql_file, top_n): # diese Funktion wird ausgeführt, wenn das script gestartet wird
    """
    find flats in a given location.

    main steps:
    1) get input sentence from the user; normalize upper/lowercase
    2) extract the location name from the user input
    3) query sql_file for flats in the given location
    4) print the top_n results
    """

    # (Step 0: make sure sql_file exists)
    if not isfile(sql_file):
        # raise an error if the file is not found
        raise FileNotFoundError(
            'Die Datei {} konnte nicht gefunden werden!'.format(sql_file)
            )

    #########################################
    # STEP 1: say hi and ask for user input #
    #########################################

    print('Hallöchen!\n')

    # print available neighbourhoods
    neighbourhoods = [
        'Charlottenburg-Wilm.', 'Friedrichshain-Kreuzberg',
        'Lichtenberg', 'Marzahn - Hellersdorf', 'Mitte', 'Neukölln', 'Pankow',
        'Reinickendorf', 'Spandau', 'Steglitz - Zehlendorf',
        'Tempelhof - Schöneberg', 'Treptow - Köpenick']
    print('Wir haben Appartements in folgenden Stadtteilen:')
    print(', '.join(neighbourhoods)) # liste wird zu einem String gemacht

    # get query from user / usereingabe wird als var gespeichert
    q1 = input('\nMöchtest du nach Stadtteil oder Preis suchen?\n')
    # normalize to lowercase / wird kleingeschrieben übernommen, da location_regex alles kleingeschrieben braucht (es müssen weniger Fälle bedacht werden)
    q1 = q1.lower()



    #####################################################################
    # STEP 2: extract location information and check whether it's valid #
    #####################################################################



    # NLU -SPRACHVERSTEHEN 

    # bekommt eingabe und muss informationen rausnehmen

    if q1 == 'stadtteil':
        # extract location from user input
        sentence = input('\nWo möchtest du übernachten?\n')
        sentence = sentence.lower()
        location = get_location_from_input(sentence)

        while location is None: # aus der if-loop ist eine while-loop gemacht worden, damit die frage immer wieder gestellt wird,bis eine zufriedenstellende antwort gegeben wurde
            # if the user input doesn't contain valid location information:
            # apologize & quit
            print('\nEntschuldigung, das habe ich leider nicht verstanden...')
            sentence = input('\nWo möchtest du denn übernachten?\n')
            sentence = sentence.lower()
            location = get_location_from_input(sentence)

            # get matches from csv file
        columns = ['name', 'neighbourhood', 'price'] # versteh ich nicht
        results = query_sql(
                key='neighbourhood_group', value=location, # es wird in neighbourhood_group nach der location gesucht
                columns=columns, sql_file=sql_file
        )

        # if there are no results: apologize & quit
        if len(results) == 0:
            print('Tut mir Leid, ich konnte leider nichts finden!')
            return

        print('Ich habe {} passende Wohnungen in {} gefunden.\n'.format(
        len(results), location))
        print('Hier sind die {} besten Ergebnisse:\n'.format(top_n))


    # print the first top_n entries from the results list
        for r in results[:top_n]: # für jeden der top 10 Einträge wird der Satz geprinted und mit name, neighbourhood und price gefüllt
            answer = '"{}", {}. Das Apartment kostet {}€.'.format(
                # look at the columns list to see what r[0], r[1], r[2] are referring to! r[0] = name / r[1] = neighborhood / r[2] = price
                r[0], r[1], r[2] 
            )
            print(answer)
        weiter_fragen(results,top_n)



    elif q1 == 'preis':
        q2 = input('\nWie groß ist dein Budget?\n')
        max_money = get_max_money_from_input(q2)

        columns = ['name', 'neighbourhood', 'price','neighbourhood_group']
        results = query_sql(
                key='price', value=max_money, 
                columns=columns, sql_file=sql_file)
        print('Ich habe {} passende Wohnungen für genau {}€ gefunden.\n'.format(
        len(results), max_money))
        print('Hier sind die besten 10 Ergebnisse:')

        while len(results) == 0:
            print('Tut mir Leid, ich konnte leider nichts finden!')
            qw = input('\nMöchtest du nach einer anderen Preisklasse suchen?\n')
            if qw == 'ja':
                q2 = input('\nWie groß ist dein Budget?\n')
                max_money = get_max_money_from_input(q2)
                columns = ['name', 'neighbourhood', 'price','neighbourhood_group'] 
                results = query_sql(
                key='price', value=max_money,
                columns=columns, sql_file=sql_file)
                print('Ich habe {} passende Wohnungen für genau {}€ gefunden.\n'.format(
                len(results), max_money))
                print('Hier sind die 10 besten Ergebnisse:')

            if qw == 'nein':
                print('Dann kann ich dir auch nicht mehr helfen.')
                return


        for r in results[:top_n]: # für jeden der top 10 Einträge wird der Satz geprinted und mit name, neighbourhood und price gefüllt
            answer = '"{}", Im Stadtteil {}.'.format(
                # look at the columns list to see what r[0], r[1], r[2] are referring to! r[0] = name / r[1] = neighborhood / r[2] = price
                r[0], r[3]
            )
            print(answer)
        weiter_fragen(results,top_n)






    # else:
    #     print('Sorry, das steht nicht zur Auswahl. Du musst dich schon für eins entscheiden.')








    #####################################################################
    # STEP 3: query sqlite file for flats in the area given by the user #
    #####################################################################




    #############################################################################
    # STEP 4: print information about the first top_n flats in the results list #
    #############################################################################

    # NLG- Sprachgenerierung

    # return results


    #############################################################################
    # STEP 5: ? #
    # Wie geht es weiter? nach Preiskategorie suchen? Dann die Option zwischen Stadtteil und Preis oder nach Stadtteil dann Preis fragen?
    # Bei Preis, müsste die Daten anders gespeichert werden, damit sie sortiert werden können? vom niedrigsten zum höchsten Preis
    # sortierung nach minimum_nights? kurztrip, urlaub, langzeit
    # Möglichkeit mehr Ergebnisse zu zeigen? ja -> die nächsten 10, nein -> verabschieden
    # Nutzer kann sich für eins der Listings entscheiden, dann wird der host_name + host_id ausgegeben? 
    # Aufforderung zur Bewertung? Auf Skala von 1 - 10. Je nachdem wie hoch dann eine Antwort
    # Personalisieren -> nach begrüßung nach Namen Fragen und dann verwenden?
    #  Smalltalk? -> tuple mit antwortmöglichkeiten?
    #############################################################################


        


if __name__ == '__main__':
    #  the airbnb_bot() function is called if the script is executed!
    airbnb_bot(sql_file='listings.db', top_n=10) # argumente: angeben, welche sql datei verwendet werden soll, wie viele ergebnisse angezeigt werden sollen
