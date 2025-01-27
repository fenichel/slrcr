import json
import urllib
import contextlib
import time
from datetime import datetime
from operator import itemgetter
import csv
import math

url = "http://www.worldsolarchallenge.org/api/positions"
csv_filename = "C:\Users\Zanzibar\Downloads\wsc_Elevation_profile.csv"
output_filename = "C:\Users\Zanzibar\Desktop\SLRCR"

class SLRCR:
    def __init__(self, name):
        self.name = name
        self.prev_time = datetime.utcnow()
        self.prev_dist = 0.0
        self.cur_time = datetime.utcnow()
        self.cur_dist = 0.0
        self.estimated_dist = 0.0
        self.position = ''
        self.lat = 0.0
        self.long = 0.0
        #don't start at 0--that holds the labels for the columns
        self.race_data_index = 1
        self.cur_race_distance = 0.0
        self.prev_race_distance = 0.0

    def update(self, data):
        if self.position != getPosition(data):
            self.position = getPosition(data)
            self.prev_dist = self.cur_dist
            self.prev_time = self.cur_time
            self.cur_time = getTime(data)
            self.cur_dist = getDist(data)
            self.estimated_dist = self.cur_dist
            self.lat = data.get(u'lat')
            self.long = data.get(u'lng')
            self.race_data_index = getRaceDataIndex(self.race_data_index,
                self.lat, self.long)
            self.prev_race_distance = self.cur_race_distance
            self.cur_race_distance = getRaceDistance(self.race_data_index)

            #print "New position for team " + self.name
            #print getPosition(data) + ", distance " + str(getDist(data))
        else:
            if self.cur_dist != 0.0 and self.prev_dist != 0.0:
                self.estimated_dist = computeTeamPosition(self.prev_dist, self.prev_time,
                    self.cur_dist, self.cur_time, datetime.utcnow())
                self.estimated_race_distance =  computeTeamPosition(
                    self.prev_race_distance, self.prev_time,
                    self.cur_race_distance, self.cur_time, datetime.utcnow())
            #print("Position didn't change. " + self.name + " is probably at "
            #+ str(self.estimated_dist))

    def getStaleness(self):
        return datetime.utcnow() - self.cur_time

    def getName(self):
        return self.name

    def getEstimatedDistance(self):
        return self.estimated_dist

    def getRaceDistance(self):
        return self.cur_race_distance

    def getRaceIndex(self):
        return self.race_data_index

def getTeams():
    teams = {}
    with contextlib.closing(urllib.urlopen(url)) as response:
        data = json.loads(response.read())

        for item in data:
            team_name = item.get(u'name')
            teams[team_name] =  SLRCR(team_name)
    return teams

def updateAll():
    with contextlib.closing(urllib.urlopen(url)) as response:
        data = json.loads(response.read())
        for item in data:
            team_name = item.get(u'name')
            if team_name in team_info:
                team_info[team_name].update(item)
            else:
                team_info[team_name] = SLRCR(team_name)

def getStanfordData():
    with contextlib.closing(urllib.urlopen(url)) as response:
        data = json.loads(response.read())

        for item in data:
            if item.get(u'name') == u'Stanford Solar Car Project':
                return item

# as a string
def getPosition(item):
    return str(item.get(u'lat')) + ', ' + str(item.get(u'lng'))

# as a float
def getDist(item):
    return item.get(u'dist_darwin')

# as a datetime
def getTime(item):
    strtime = item.get(u'gps_when')
    dt = datetime.strptime(strtime, "%Y-%m-%d %H:%M:%S")
    return dt

def computeTeamPosition(old_position, old_time, new_position, new_time, cur_time):
    time_diff = (new_time - old_time).total_seconds() / 3600
    speed = (new_position - old_position) / time_diff
    cur_position = new_position + speed * ((cur_time - new_time).total_seconds() / 3600)
    return cur_position

def rankTeams():
    ranking = []
    for key, value in team_info.iteritems():
        #ranking.append((key, value.getEstimatedDistance()))
        ranking.append((key, value.getRaceIndex(), value.getStaleness()))
    ranking.sort(key=itemgetter(1), reverse=True)
    return ranking

def printRanking(ranking):
    for i in range(len(ranking)):
        rd_index = ranking[i][1]
        outstr = (str(i) + ") " +  ranking[i][0] + ": " + race_data[rd_index][0] 
        + "\t\tstaleness: " + str(ranking[i][2]))
        print outstr

        outstr = (outstr + " \test location " + str(race_data[rd_index][1]) + ", "
        + str(race_data[rd_index][2])) + "\r\n"
        #print outstr
        output_file.write(outstr)
    output_file.write("############################################\r\n")

def distanceBetween(lat_a, long_a, lat_b, long_b):
    return math.fabs((math.sqrt(lat_a * lat_a + long_a * long_a) -
    math.sqrt(lat_b * lat_b + long_b * long_b)))

def getRaceDataIndex(start_index, cur_lat, cur_long):
    for i in range(start_index, len(race_data)):
        line = race_data[i]
        read_lat = line[1]
        read_long = line[2]
        if (distanceBetween(cur_lat, cur_long, float(read_lat), float(read_long)) <  0.01):
            return i

def getRaceDistance(index):
    return float(race_data[index][0])

def loadRaceData():
    with open(csv_filename, 'rU') as f:
        reader = csv.reader(f)
        return list(reader)

output_file = open(output_filename, "ab")
race_data = loadRaceData()
team_info = getTeams()
print team_info

for i in range(120):
    updateAll()
    printRanking(rankTeams())
    print "############################################"
    time.sleep(60)