import geoip2.database

reader = geoip2.database.Reader('geoip/GeoLite2-City.mmdb')

def get_location(ip):

    try:
        response = reader.city(ip)

        country = response.country.name
        city = response.city.name

        return f"{city}, {country}"

    except:
        return "Unknown Location"
