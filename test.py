import datetime
import pytz
import bson

utc_now = datetime.datetime.utcnow()
utc_tz = pytz.timezone('UTC')


ny_tz = pytz.timezone('America/New_York')
ny_now = utc_tz.localize(utc_now).astimezone(ny_tz)


current_date = datetime.datetime.utcnow()
bson_date = bson.datetime.datetime(current_date.year, current_date.month, current_date.day,
                                    current_date.hour, current_date.minute, current_date.second)
print(bson_date)