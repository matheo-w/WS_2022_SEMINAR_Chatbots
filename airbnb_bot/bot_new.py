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
    (r'(haus)|(wohnung)|(apartment)','Entire home/apt'),
    (r'((privat)|(eigenes)|(zimmer))', 'Private Room'),
    (r'(gruppen)|(gemeinsames)|(geteiltes)', 'Shared Room')

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


def query_sql(key, value, columns, sql_file):
    """
    Query a sqlite file for entries where "key" has the value "value".
    Return the values corresponding to columns as a list.
    """

    # set up sqlite connection
    conn = sql.connect(sql_file)
    c = conn.cursor()


    # prepare query string
    #query_template = 'SELECT {columns} FROM listings WHERE {key} = "{value}"'
    query_template = 'SELECT {columns} FROM listings WHERE neighbourhood_group = location AND price = max_price AND minimum_nights = min_nights AND room_type = room_t'

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

    # get query from user
    sentence = input('\nWo möchtest du denn übernachten?\n')
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
    answer = 'Also dann in {}'.format(location)
    print(answer)

    sentence2 = input('\nWas für eine Unterkunft suchst du? Wir haben Häuser/Wohnungen,Einzelzimmer oder geteilte Zimmer zur verfügung.\n')
    sentence2 = sentence2.lower()
    room_t = get_location_from_input(sentence2, regex_list=room_regex)

    while room_t is None:
        print('\nEntschuldigung, das habe ich leider nicht verstanden...')
        sentence2 = input('\nWas für eine Unterkunft suchst du? Wir haben Häuser/Wohnungen,Einzelzimmer oder geteilte Zimmer zur verfügung.\n')
        sentence2 = sentence2.lower()
        room_t = get_location_from_input(sentence2, regex_list=room_regex)
    answer2 = 'Also dann ein {}'.format(room_t)
    print(answer2)



    



  

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