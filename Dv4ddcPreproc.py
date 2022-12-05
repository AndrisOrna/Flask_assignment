def apply_all(df):
    # df["Mileage"] = df["Mileage"].apply(mileagePreproc)
    df["Price"] = df["Price"].apply(pricePreproc)
    # df["Make"] = df["Make"].apply(makePreproc)
    df["Year"] = df["Year"].apply(yearPreproc)
    return df

def mileagePreproc(milage):

    if milage == "---": return float('NaN')
    if type(milage) is float: return milage

    if " " in milage:
        num_str, unit = milage.split(" ")
    else:
        num_str = milage
    # remove ","

    num_str = num_str.replace(",", "")

    # Convert to integer

    print(num_str)
    try:
        num = float(num_str)
    except:
        num = -1.0
    # if "km" in unit:
    #     pass
    # elif "mi" in milage:
    #     num *= 1.60934

    return num

def pricePreproc(price):

    if type(price) == int or type(price) == float:
        return float(price) 
    
    if "No" in price:
        return float('NaN')

    # £1,100
    price = price.replace(",", "")
    # £1100
    if "$" in price:
        price = price.replace("$", " ")
        
        # "1100"
        # price = int(price) * 1.15 
    # elif "€" in price:
    #     price = price.replace("€", "")
    #     price = int(price)

        return price

def makePreproc(make):

    make = make.replace(" ", "")

    make = make.upper()
    if "---" in make:
        make = "Other"
    if "VW" in make:
        make = "Volkswagen"
    return make

def yearPreproc(year):
    if type(year) is float:
        return -4
    if year == "---":
        return -4
    return int(year)



def country_of_registrationProc(country_of_registration):
    if country_of_registration == "UK":
        country_of_registration = "United Kingdom"
    if country_of_registration == "---":
        country_of_registration = "Other"

    return country_of_registration

def countyPreproc(county):
    
    county = county.replace(" Town", "")
    county = county.replace(" City", "")
    counties = county.split(", ")
    if len(counties) > 1:
        return counties[1]
    return county
