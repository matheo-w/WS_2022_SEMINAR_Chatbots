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


def query_sql(key, value, columns, sql_file):
    """
    Query a sqlite file for entries where "key" has the value "value".
    Return the values corresponding to columns as a list.
    """

    # set up sqlite connection
    conn = sql.connect(sql_file)
    c = conn.cursor()


    # prepare query string
    query_template = 'SELECT {columns} FROM listings WHERE {key} = "{value}"'
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

    #####################################################################
    # STEP 2: extract location information and check whether it's valid #
    #####################################################################



    # NLU -SPRACHVERSTEHEN

    # extract location from user input
    location = get_location_from_input(sentence)

    if location is None:
        # if the user input doesn't contain valid location information:
        # apologize & quit
        print('\nEntschuldigung, das habe ich leider nicht verstanden...')
        return

    #####################################################################
    # STEP 3: query sqlite file for flats in the area given by the user #
    #####################################################################

    # get matches from csv file
    columns = ['name', 'neighbourhood', 'price']
    results = query_sql(
            key='neighbourhood_group', value=location,
            columns=columns, sql_file=sql_file
        )

    # if there are no results: apologize & quit
    if len(results) == 0:
        print('Tut mir Leid, ich konnte leider nichts finden!')
        return


    #############################################################################
    # STEP 4: print information about the first top_n flats in the results list #
    #############################################################################

    # NLG- Sprachgenerierung

    # return results
    print('Ich habe {} passende Wohnungen in {} gefunden.\n'.format(
        len(results), location))
    print('Hier sind die {} besten Ergebnisse:\n'.format(top_n))

    # print the first top_n entries from the results list
    for r in results[:top_n]:
        answer = '"{}", {}. Das Apartment kostet {}€.'.format(
            # look at the columns list to see what r[0], r[1], r[2] are referring to!
            r[0], r[1], r[2]
        )
        print(answer)


    sentence2 = input('\nMöchtest du 10 weitere Ergebnisse sehen?\n')
    sentence2 = sentence2.lower()

    if sentence2 == 'ja': # mehr antwortmöglichkeiten anbieten?
        print('Hier sind die {} besten Ergebnisse:\n'.format(top_n))
        for r in results[10:20]:
            answer = '"{}", {}. Das Apartment kostet {}€.'.format(r[0], r[1], r[2])
            # look at the columns list to see what r[0], r[1], r[2] are referring to! r[0] = name / r[1] = neighborhood / r[2] = price
            print(answer)
    else:
        print('Dann halt nicht.')
        return


if __name__ == '__main__':
    #  the airbnb_bot() function is called if the script is executed!
    airbnb_bot(sql_file='listings.db', top_n=10)
