"""JSON Options"""

import json

import requests

# pylint: disable=unspecified-encoding, too-many-arguments, too-many-locals, too-many-return-statements,
# pylint: disable=too-many-return-statements,too-many-branches,too-many-statements,duplicate-code,line-too-long


def show_options(
    product, equities_selection=None, country=None, sector=None, industry=None
):
    """
    Description
    ----
    Returns all options that exist in the database that you can use to filter the database.
    In case you use country and/or sector, you obtain different lists based on your input.
    The industry variable is a boolean that returns all industries, to what sector each
    corresponds and all countries that have companies in this industry.

    Input
    ----
    product (string)
        Gives all data for a specific product which can be
        cryptocurrencies, currencies, equities, etfs or funds.
    equities_selection (string)
        Gives a sub selection of the possibilities for equities which can be countries, sectors or
        industries.
    country (string)
        By entering a country here, you are able to obtain all Sectors and Industries within
        this country. You can add in Sector to specify on the Industry level.
    sector (string)
        By entering a sector here, you are able to obtain all industries within this sector. You can
        add in country to specify within a country.
    industry (boolean)
        By setting industry to True, you are able to obtain the sector the industry resides
        in as well as all countries who have companies in this industry.

    Output
    ----
    json_data (dictionary)
        Returns a dictionary with a selection based on the input.
    """
    url = (
        "https://raw.githubusercontent.com/JerBouma/FinanceDatabase/main/"
        "Database/Categories/"
    )

    if country or sector or industry is not None:
        if product.lower() != "equities":
            print(
                "Country, sector and industry variables only work for equities thus changing the "
                "product to equities."
            )
            product = "equities"

        equities_url = (
            "https://raw.githubusercontent.com/JerBouma/FinanceDatabase/main/"
            f"Database/{product.capitalize()}"
        )
        if industry:
            if country or sector is not None:
                print(
                    "Industry parameter is set to True thus ignoring country and sector parameters."
                )
            try:
                json_file = f"{equities_url}/Industries/_Industries Countries.json"
                request = requests.get(json_file, timeout=30)
                json_data = json.loads(request.text)
            except json.decoder.JSONDecodeError:
                print("Not able to find any data for industries.")
                return {}
        elif country and sector:
            try:
                country = country.replace("%", "%25").replace(" ", "%20")
                sector = sector.replace("%", "%25").replace(" ", "%20")
                json_file = f"{equities_url}/Countries/{country}/{sector}/_{sector} Industries.json"
                request = requests.get(json_file, timeout=30)
                json_data = json.loads(request.text)
            except json.decoder.JSONDecodeError:
                print(
                    f"Not able to find any data with the combination of Country ({country}) "
                    f"and Sector ({sector})"
                )
                return {}
        elif country:
            json_data = {}
            try:
                country = country.replace("%", "%25").replace(" ", "%20")

                json_file = f"{equities_url}/Countries/{country}/{country} Sectors.json"
                request = requests.get(json_file, timeout=30)
                sector = json.loads(request.text)
                json_data["Sectors"] = sector

                json_file = (
                    f"{equities_url}/Countries/{country}/{country} Industries.json"
                )
                request = requests.get(json_file, timeout=30)
                industries = json.loads(request.text)
                json_data["Industries"] = industries
            except json.decoder.JSONDecodeError:
                print(f"Not able to find any data for {country}.")
                return {}
        elif sector:
            try:
                sector = sector.replace("%", "%25").replace(" ", "%20")
                json_file = f"{equities_url}/Sectors/{sector}/_{sector} Countries and Industries.json"
                request = requests.get(json_file, timeout=30)
                json_data = json.loads(request.text)
            except json.decoder.JSONDecodeError:
                print(f"Not able to find any data for {sector}.")
                return {}
    else:
        if product.lower() not in [
            "cryptocurrencies",
            "currencies",
            "equities",
            "etfs",
            "funds",
        ]:
            raise ValueError(
                f"{product.lower()} is not an available option. Please choose either "
                "'cryptocurrencies', 'currencies', 'equities', 'etfs' or 'funds'."
            )
        if equities_selection is not None:
            if equities_selection.lower() not in ["countries", "sectors", "industries"]:
                raise ValueError(
                    f"{equities_selection.lower()} is not an available sub selection. "
                    "Please choose either 'countries', 'sectors' or 'industries'."
                )
            if (
                equities_selection.lower() in ["countries", "sectors", "industries"]
                and product.lower() != "equities"
            ):
                print(
                    "equities_selection is only used for the product 'equities' thus "
                    "changing product to 'equities'."
                )
                product = "equities"

        try:
            if product.lower() == "equities" and equities_selection is None:
                json_data = {}
                for option in ["countries", "sectors", "industries"]:
                    json_file = f"{url}{product.lower()}_{option}.json"
                    request = requests.get(json_file, timeout=30)
                    json_data[option] = json.loads(request.text)
                return json_data
            if equities_selection:
                json_file = f"{url}{product.lower()}_{equities_selection}.json"
            else:
                json_file = f"{url}{product.lower()}_options.json"
            request = requests.get(json_file, timeout=30)
            json_data = json.loads(request.text)
        except json.decoder.JSONDecodeError:
            print(f"Not able to find the options for {product.lower()}.")
            return {}

    return json_data


def search_products(
    database, query, search="summary", case_sensitive=False, new_database=None
):
    """
    Description
    ----
    Search in the provided dictionary for a specific query. By default
    it searches in the 'summary' key which can be found in equities, etfs and funds.

    Input
    ----
    database (dictionary)
        A dictionary that has data from the Database.
    query (string)
        The search term that is used to search in the dictionary.
    search (string):
        The key of the dictionary you wish to search in. The default
        is set to 'summary'.
    case_sensitive (boolean):
        A variable that determines whether the query needs to be case
        sensitive or not. Default is False.
    new_database (dictionary, default is None)
        If filled, is used to add data to based on the query.

    Output
    ----
    json_data (dictionary)
        Returns a dictionary with a selection based on the input.
    """
    if new_database is None:
        new_database = {}

    try:
        all_keys = list(database[list(database.keys())[0]].keys())
    except IndexError:
        print(
            "The database is empty. Please fill the database with one of the 'select' functions."
        )
        return {}
    if search not in all_keys:
        print(
            f"The value {search} is not an option for the 'search' variable. "
            f"Please select one of the following:\n{all_keys}"
        )
        return {}

    for symbol in database:
        try:
            string = database[symbol][search]
            if not case_sensitive:
                query = query.lower()
                string = database[symbol][search].lower()
            if query in string:
                new_database[symbol] = database[symbol]
        except (TypeError, KeyError, AttributeError):
            continue

    return new_database
