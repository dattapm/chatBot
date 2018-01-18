import sys
sys.path.append('/opt/lessenger')

print "IN welcome API"

from welcome.welcome import Welcome

application = Welcome()
