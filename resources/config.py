MONGO_CONNECTION = 'mongodb+srv://covidUser:covidPassword@maincluster.lgijy.mongodb.net/theDB?retryWrites=true&w=majority'
DB_NAME = 'theDB'

help_seeker_collection = "help_seeker"
help_giver_collection = "help_giver"


class HelpTypes:
    oxygen = "oxygen"
    bed = "bed"
    vaccine = "baccine"
    covid_test = "covid_test"
    other = "other"
