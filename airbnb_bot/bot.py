import re
import sqlite3 as sql
from os.path import isfile



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

room_regex = [
    (r'(haus)|(wohnung)|(apartment)|(palast)|(flat)|(loft)','Entire home/apt'),
    (r'(privat)|(eigenes)|(einzel)|(zimmer)|(room)', 'Private Room'),
    (r'(gruppen)|(gemeinsames)|(geteilt)|(wg)|(wohngemeinschaft)|(gemeinschaft)|(shared)', 'Shared Room')

]

filter_regex = [
    (r'(teuer)|(absteigend)|(hoch)|(höchste)', 'dem höchsten Preis'),
    (r'(günstig)|(billig)|(aufsteigend)|(niedrig)', 'dem niedrigsten Preis'),
    (r'(bewertung)|(bewert)|(beste)|(meist)|(viel)', 'den meisten Bewertungen')
]

retry_regex = [
    (r'(ja)|(yes)|(positiv)|(in der tat)|(auf jeden fall)|(bitte)', 'Ja'),
    (r'(nein)|(no)|(negativ)|(niemals)|(auf keinen fall)|(nicht)|(lass mich)', 'Nein')
]




def get_location_from_input(sentence, regex_list):
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

# def get_room_from_input(sentence, regex_list=room_regex):

#     for regex, value in regex_list

#def query_sql(location, max_price, min_nights, room_t, columns, sql_file):

def query_sql(key, value, room_t, max_price, min_nights, columns, sql_file):
    """
    Query a sqlite file for entries where "key" has the value "value".
    Return the values corresponding to columns as a list.
    """

    # set up sqlite connection
    conn = sql.connect(sql_file)
    c = conn.cursor()


    # prepare query string
    query_template = 'SELECT {columns} FROM listings WHERE {key} = "{value}" AND room_type = "{room_t}" AND price <= {max_price} and minimum_nights <= {min_nights}'
    #query_template = 'SELECT {columns} FROM listings WHERE neighbourhood_group = "{location}" AND room_type = "{room_t}"'
    #query_template = 'SELECT * from listings WHERE neighbourhood_group = {location} AND room_type = {room_t}'
    #query_template = 'SELECT {columns} FROM listings WHERE neighbourhood_group = {location} AND price = {max_price} AND minimum_nights = {min_nights} AND room_type = {room_t}'


    columns_string = ', '.join(columns)  # e.g. [location, price] -> 'location, price'
    # replace the curly brackets in query_template with the corresponding info
    query = query_template.format(columns=columns_string, key=key, value=value, room_t=room_t, max_price=max_price, min_nights=min_nights)
    #query = query_template.format(columns=columns_string, neighbourhood_group=location, room_type=room_t )
   # query = query_template.format(columns=columns_string, location=location, max_price = max_price,min_nights=min_nights, room_t=room_t )



    # execute query
    r = c.execute(query)
    # get results as list
    results = r.fetchall()

    # close connection
    conn.close()

    return results


def airbnb_bot(sql_file, top_n):
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
    print(', '.join(neighbourhoods))

    active = True
    filter_status = True
    price_status = True
    nights_status = True
  
    
    # get query from user
    while active == True:

#-----------------------------------------------------------------------------------------------------------
# Ortsabfrage
        sentence = input('\nWo soll die Reise denn hingehen?\n')
        # normalize to lowercase
        sentence = sentence.lower()

        # extract location from user input
        location = get_location_from_input(sentence,regex_list=location_regex)

        while location is None:
            # if the user input doesn't contain valid location information:
            # apologize & quit
            print('\nEntschuldigung, das habe ich leider nicht verstanden...')
            sentence = input('\nWo möchtest du denn übernachten?\n')
            sentence = sentence.lower()
            location = get_location_from_input(sentence, regex_list=location_regex)
        answer = '\n {}? Da würde ich nicht bleiben wollen, aber okay... Ist ja dein Ausflug ne?\n'.format(location)
        print(answer)
#-----------------------------------------------------------------------------------------------------------
# Art der Unterkunft

        sentence2 = input('Was für eine Unterkunft suchst du? Ich kann nach Häusern bzw. Wohnungen, Einzelzimmern oder WG Zimmern suchen.\n')
        sentence2 = sentence2.lower()
        room_t = get_location_from_input(sentence2, regex_list=room_regex)

        while room_t is None:
            print('\nSorry, das habe ich leider nicht verstanden...')
            sentence2 = input('\nWas für eine Unterkunft suchst du? Wir haben Häuser/Wohnungen,Einzelzimmer oder geteilte Zimmer zur verfügung.\n')
            sentence2 = sentence2.lower()
            room_t = get_location_from_input(sentence2, regex_list=room_regex)

        if room_t == 'Entire home/apt':
            print('\nHast wohl gern viel Platz? Vielleicht ist Berlin dann ehrlich gesagt nicht die beste Option für dich... Aber egal, machen wir weiter!')
        if room_t == 'Private Room':
            print('\nIst immer noch günstiger als ein Hotel, ne?')
        if room_t == 'Shared Room':
            print('\nMutige Entscheidung. Ich warne dich schonmal vor, davon werden garnicht so viele Angeboten!')

#-----------------------------------------------------------------------------------------------------------
# Frage nach dem Budget
        while price_status == True:
            price_input = input('\nWas würdest du denn ausgeben wollen?\n') #gibt man 3oo oder ähnliches ein kommt ein fehler. buchstaben direkt nach den zahlen sind gefährlich, weiß aber nicht warum. Das €-Zeichen direkt danach funktioniert aber
            p = ''.join(price_input)
            p_txt = re.findall(r'\b[0-9]+\b', p)
            max_price = ''.join(p_txt)

            try:
                val = int(max_price)
                price_status = False
            except ValueError:
                print('\nGibt dein Budget bitte als Zahl ein. Du darfst aber gern noch was nettes dazuschreiben ;)')
                price_status = False
                price_status = True


        if int(max_price) < 50:
            answer3 = '\n Nur {}€? Ich hoffe für dich es gibt auch günstige Angebote'.format(max_price)
        else:
            answer3 = '\n Dein Budget liegt also bei {}€. Interessant... Bist also kein Geringverdiener! Ich suche dir etwas aus das in dein Budget passt.'.format(max_price)
        print(answer3)

#-----------------------------------------------------------------------------------------------------------
# Länge des Aufenthalts
    
        while nights_status == True:
            nights_input = input('\nWie lange möchtest du bleiben? Bitte keine Angaben in Wochen, ich bin schlecht im rechnen :(\n')
            n = ''.join(nights_input)
            n_txt = re.findall(r'\b[0-9]+\b', n)
            min_nights = ''.join(n_txt)

            try:
                val = int(min_nights)
                nights_status = False
            except ValueError:
                print('\nGib die länge deines Aufenthalts bitte als ganze Zahl ein :(')
                nights_status = False
                nights_status = True


        if int(min_nights) <= 3:
            answer4 = '\n Ein Wochenendausflug? Nett.\n'
        if int(min_nights) >= 4:
            answer4 = '\n {} Tage? Das sollte lang genug sein um sich alles anzuschauen!\n'.format(min_nights)
        print(answer4)
            
#-----------------------------------------------------------------------------------------------------------
# Ergebnisse

        columns = ['name', 'neighbourhood', 'price', 'minimum_nights', 'room_type', 'neighbourhood_group', 'number_of_reviews','host_name']
        results = query_sql(
            key='neighbourhood_group', value=location, room_t=room_t, max_price=max_price, min_nights=min_nights,
            columns=columns, sql_file=sql_file)
#-----------------------------------------------------------------------------------------------------------
# Falls nichts gefunden wurde, suche nochmal starten:

        print(' Ich habe {} passende {} in {} gefunden.'.format(
                    len(results),room_t ,location))
        if len(results) == 0:
            print('\n Sieht so aus als könnte ich dir nichts anbieten... Vielleicht klappts ja in einem anderen Stadtteil?')
            active = False
            retry = input('\nMöchtest du nochmal eine neue Suche starten?\n')
            retry = retry.lower()
            retry_a = get_location_from_input(retry, regex_list=retry_regex)
            while retry_a is None:
                print(' Es gibt nur diese zwei Möglichkeiten!')
                retry = input('\nMöchtest du nochmal eine neue Suche starten?\n')
                retry = retry.lower()
            retry_a = get_location_from_input(retry, regex_list=retry_regex)
            if retry_a == 'Ja':
                active = True
                nights_status = True
                price_status = True
            else:
                print('\n Sorry dass ich dir nicht helfen konnte, kannst ja zur Not im Auto schlafen!\n')
            
#-----------------------------------------------------------------------------------------------------------
# Wenn Ergbnisse da sind, können diese unterschiedlich gefiltert ausgegeben werden:
        else:
            filter_status = True
            while filter_status == True:
                filter_q = input('\nMöchtest du die günstigsten, teuersten oder am häufigsten bewertesten Ergebnisse sehen?\n')
                filter_q = filter_q.lower()
                filter_a = get_location_from_input(filter_q, regex_list=filter_regex)

                while filter_a is None:
                    print('\nSorry, das hab ich nicht ganz verstanden, versuchen wir es nochmal')
                    filter_q = input('\nMöchtest du die günstigsten, teuersten oder am häufigsten bewertesten Ergebnisse sehen?\n')
                    filter_q = filter_q.lower()
                    filter_a = get_location_from_input(filter_q, regex_list=filter_regex)
                
                for r in results[:top_n]:
                    answer_filter='\n Hier sind die top {} Ergebnisse mit {} für {} in {}:\n'.format(top_n,filter_a, r[4], r[5])
                print(answer_filter)

#-----------------------------------------------------------------------------------------------------------
                if filter_a == 'den meisten Bewertungen':
                
                    results.sort(reverse= True, key=lambda y: y[6])

                    for r in results[:top_n]:
                        answer = '"{}" wird angeboten von {}. Der Preis pro Nacht liegt bei {}€. Es gibt insgesamt {} Reviews.\n'.format(r[0],r[7],r[2],r[6])
                        active = False
                        filter_status = False
                    restart_filter = input('\nMöchtest du die Ergebnisse anders sotrieren?\n')
                    restart_filter = restart_filter.lower()
                    r_filter = get_location_from_input(restart_filter, regex_list=retry_regex)

                    while r_filter is None:
                        print('\nDrück dich bitte klarer aus! Ja oder nein?')
                        restart_filter = input('\nMöchtest du die Ergebnisse anders sotrieren?\n')
                        restart_filter = restart_filter.lower()
                        r_filter = get_location_from_input(restart_filter, regex_list=retry_regex)
                    if r_filter == 'Ja':
                        filter_status = True
                    if r_filter == 'Nein':
                        retry = input('\nMöchtest du nochmal eine neue Suche starten?\n')
                        retry = retry.lower()
                        retry_a = get_location_from_input(retry, regex_list=retry_regex)

                        if retry_a == 'Ja':
                            active = False
                            active = True
                            nights_status = True
                            price_status = True
                            filter_status = False

                        else:
                            print('\nAlles klar, ich hoffe da war was für dich dabei! Gute Reise!')
                            filter_status = False

#-----------------------------------------------------------------------------------------------------------
                if filter_a == 'dem höchsten Preis':

                    results.sort(reverse=True, key=lambda y: y[2])

                    for r in results[:top_n]:
                        answer = '"{}" wird angeboten von {}. Der Preis pro Nacht liegt bei {}€. Es gibt insgesamt {} Reviews.\n'.format(r[0],r[7],r[2],r[6])
                        print(answer)
                        active = False
                        filter_status = False
                    restart_filter = input('\nMöchtest du die Ergebnisse anders sotrieren?\n')
                    restart_filter = restart_filter.lower()
                    r_filter = get_location_from_input(restart_filter, regex_list=retry_regex)
                    while r_filter is None:
                        print('\nDrück dich bitte klarer aus! Ja oder nein?')
                        restart_filter = input('\nMöchtest du die Ergebnisse anders sotrieren?\n')
                        restart_filter = restart_filter.lower()
                        r_filter = get_location_from_input(restart_filter, regex_list=retry_regex)
                    if r_filter == 'Ja':
                        filter_status = True
                    if r_filter == 'Nein':
                        retry = input('\nMöchtest du nochmal eine neue Suche starten?\n')
                        retry = retry.lower()
                        retry_a = get_location_from_input(retry, regex_list=retry_regex)

                        if retry_a == 'Ja':
                            active = False
                            active = True
                            nights_status = True
                            price_status = True
                            filter_status = False

                        else:
                            print('\nAlles klar, ich hoffe da war was für dich dabei! Gute Reise!')
                            filter_status = False

#-----------------------------------------------------------------------------------------------------------
                if filter_a == 'dem niedrigsten Preis':

                    results.sort(key=lambda y: y[2])
                    for r in results[:top_n]:
                        answer = '"{}" wird angeboten von {}. Der Preis pro Nacht liegt bei {}€. Es gibt insgesamt {} Reviews.\n'.format(r[0],r[7],r[2],r[6])
                        print(answer)
                        active = False
                        filter_status = False
                    restart_filter = input('\nMöchtest du die Ergebnisse anders sotrieren?\n')
                    restart_filter = restart_filter.lower()
                    r_filter = get_location_from_input(restart_filter, regex_list=retry_regex)
                    while r_filter is None:
                        print('\nDrück dich bitte klarer aus! Ja oder nein?')
                        restart_filter = input('\nMöchtest du die Ergebnisse anders sotrieren?\n')
                        restart_filter = restart_filter.lower()
                        r_filter = get_location_from_input(restart_filter, regex_list=retry_regex)
                    if r_filter == 'Ja':
                        filter_status = True
                    if r_filter == 'Nein':
                        retry = input('\nMöchtest du nochmal eine neue Suche starten?\n')
                        retry = retry.lower()
                        retry_a = get_location_from_input(retry, regex_list=retry_regex)

                        if retry_a == 'Ja':
                            active = False
                            active = True
                            nights_status = True
                            price_status = True
                            filter_status = False

                        else:
                            print('\nAlles klar, ich hoffe da war was für dich dabei! Gute Reise!')
                            filter_status = False
                


    



  

    #####################################################################
    # STEP 3: query sqlite file for flats in the area given by the user #
    #####################################################################

    # get matches from csv file
    # columns = ['name', 'neighbourhood', 'price']
    # results = query_sql(
    #         key='neighbourhood_group', value=location,
    #         columns=columns, sql_file=sql_file
    #     )

    # # if there are no results: apologize & quit
    # if len(results) == 0:
    #     print('Tut mir Leid, ich konnte leider nichts finden!')
    #     return


    # #############################################################################
    # # STEP 4: print information about the first top_n flats in the results list #
    # #############################################################################

    # # NLG- Sprachgenerierung

    # # return results
    # print('Ich habe {} passende Wohnungen in {} gefunden.\n'.format(
    #     len(results), location))
    # print('Hier sind die {} besten Ergebnisse:\n'.format(top_n))

    # # print the first top_n entries from the results list
    # for r in results[:top_n]:
    #     answer = '"{}", {}. Das Apartment kostet {}€.'.format(
    #         # look at the columns list to see what r[0], r[1], r[2] are referring to!
    #         r[0], r[1], r[2]
    #     )
    #     print(answer)


if __name__ == '__main__':
    #  the airbnb_bot() function is called if the script is executed!
    airbnb_bot(sql_file='listings.db', top_n=10)