import sys
sys.path.append('/opt/lessenger')

print "IN weather API"

from weather.weather import Weather

application = Weather()
