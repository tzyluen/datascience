# -*- coding: utf-8 -*-

import sys
import re
import pprint
import json
import urllib2
import time


def create_tables():
    print '''
CREATE TABLE state (
    id INTEGER PRIMARY KEY NOT NULL,
    name CHAR(50) NOT NULL
);

CREATE TABLE constituency (
    id INTEGER PRIMARY KEY NOT NULL,
    code CHAR(4) NOT NULL,
    name CHAR(50) NOT NULL,
    state_id INTEGER NOT NULL,
    incumbent CHAR(50) NOT NULL,
    eligible_voters INTEGER NOT NULL,
    malay_voters INTEGER NOT NULL,
    chinese_voters INTEGER NOT NULL,
    indian_voters INTEGER NOT NULL,
    others_voters INTEGER NOT NULL,
    muslim_bumi_voters INTEGER NOT NULL,
    non_muslim_bumi_voters INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    FOREIGN KEY(state_id) REFERENCES state(id)
);

CREATE TABLE candidate (
    id INTEGER PRIMARY KEY NOT NULL,
    constituency_id INTEGER NOT NULL,
    name CHAR(100) NOT NULL,
    party CHAR(5) NOT NULL,
    coalition CHAR(5) NOT NULL,
    FOREIGN KEY(constituency_id) REFERENCES constituency(id)
);

CREATE TABLE result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    constituency_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    votes INTEGER NOT NULL,
    votes_p REAL NOT NULL,
    winner INTEGER,
    majority INTEGER NOT NULL,
    FOREIGN KEY(constituency_id) REFERENCES constituency(id)
    FOREIGN KEY(candidate_id) REFERENCES candidate(id)
);

CREATE TABLE stat (
    constituency_id INTEGER NOT NULL,
    voter_turnout INTEGER NOT NULL,
    voter_turnout_p REAL NOT NULL,
    spoilt_votes INTEGER NOT NULL,
    spoilt_votes_p REAL NOT NULL,
    FOREIGN KEY(constituency_id) REFERENCES constituency(id)
);

'''


def get_gps(s):
    ''' api.geonames.org '''
    '''
    params = {'placename': s, 'maxRows': 1, 'username': 'demo', 'country': 'MY'}
    url = 'http://api.geonames.org/postalCodeSearchJSON'
    '''

    ''' maps.googleapis.com '''
    SERVERKEY = 'AIzaSyCghaD9EK-Q7i_7UbW9uoaX4W8_I2t3m-o'
    s += ', MY'
    url = 'https://maps.googleapis.com/maps/api/geocode/json' + '?address=' + \
                s.replace(' ', '+') + '&key=' + SERVERKEY

    response = urllib2.urlopen(url)
    result = json.load(response)

    if result['status'] == 'OK':
        ''' api.geonames.org
        lat = result[k][0]['lat']
        lng = result[k][0]['lng']
        '''

        ''' maps.googleapis.com '''
        lat = result['results'][0]['geometry']['location']['lat']
        lng = result['results'][0]['geometry']['location']['lng']
        return { 'lat': lat, 'lng': lng }

    return False


''' string `s' is in this format: 'Zahidi Zainul Abidin (BN-UMNO)'
return a list contains ['name', 'party', 'coalition'] '''

def parse_candidate(s):
    regex_candidate = re.compile('([\w@ ]+) \((\w+)(-\w+)?\)')
    matches_candidate = regex_candidate.search(s)

    if matches_candidate:
        name = matches_candidate.group(1)
        party = matches_candidate.group(2)
        coalition = party

        if matches_candidate.group(3):
            if matches_candidate.group(3)[0] == '-':
                party = matches_candidate.group(3)[1:]

        return [name, party, coalition]

    return []


def main():
    create_tables()

    with open(sys.argv[1], 'r') as f:
        candidate_index = 0
        state_index = 0
        constituency_index = 1
        count = 0

        for line in f:
            if line in ['\n', '\r\n']:
                continue
            l = re.split("\s{2,}", line)

            if l[0][0] == '#':
                ''' line contains the state and separator '''
                state = l[0][2:].strip()
                print 'INSERT INTO state (id, name) VALUES ({}, "{}");'.format(state_index, state)
                state_index += 1

            elif l[0][0] == ';':
                ''' line contains the opponent(s) '''
                candd = parse_candidate(l[0][1:])
                votes = l[1].replace(",", "")
                tmp = l[2].strip()
                votes_p = tmp[:-1]
                if candd:
                    cname, cparty, ccoalition = [candd[0], candd[1], candd[2]]
                    print 'INSERT INTO candidate (id, constituency_id, ' \
                            'name, party, coalition) VALUES ({}, {}, ' \
                            '"{}", "{}", "{}");'.format(candidate_index,
                            constituency_index - 1, cname, cparty, ccoalition)

                    print 'INSERT INTO result (constituency_id, candidate_id, ' \
                            'votes, votes_p, winner, majority) VALUES ' \
                            '({}, {}, {}, {}, {}, {});'.format(constituency_index - 1,
                            candidate_index, votes, votes_p, 0, 0)

                    candidate_index += 1
            else:
                ''' line contains the result '''
                constituency_code = l[0]
                constituency_name = l[1]
                winner = l[2]
                votes = l[3].replace(",", "")
                votes_p = l[4][:-1]
                opponent = l[5]
                opponent_votes = l[6].replace(",", "")
                opponent_votes_p = l[7][:-1]
                majority = l[8].replace(",", "")
                incumbent = l[9]
                eligible_voters = l[10].replace(",", "")
                malay_voters = l[11][:-1]
                chinese_voters = l[12][:-1]
                indian_voters = l[13][:-1]
                others_voters = l[14][:-1]
                muslim_bumi_voters = l[15][:-1]
                non_muslim_bumi_voters = l[16][:-1]

                voter_turnout = l[17].replace(",", "")
                voter_turnout_p = l[18][:-1]
                spoilt_votes = l[19].replace(",", "")
                tmp = l[20].strip()
                spoilt_votes_p = tmp[:-1]

                ''' pull the winner and the first opponent into the `candidate` and `result` table '''

                ''' winner '''
                candd = parse_candidate(winner)
                cname, cparty, ccoalition = [candd[0], candd[1], candd[2]]
                print 'INSERT INTO candidate (id, constituency_id, name, party, ' \
                        'coalition) VALUES ({}, {}, "{}", "{}", "{}");'.format(
                        candidate_index, constituency_index, cname, cparty, ccoalition)
                print 'INSERT INTO result (constituency_id, candidate_id, ' \
                        'votes, votes_p, winner, majority) VALUES ' \
                        '({}, {}, {}, {}, {}, {});'.format(constituency_index,
                        candidate_index, votes, votes_p, 1, majority)
                candidate_index += 1

                ''' first opponent '''
                candd = parse_candidate(opponent)
                cname, cparty, ccoalition = [candd[0], candd[1], candd[2]]
                print 'INSERT INTO candidate (id, constituency_id, ' \
                        'name, party, coalition) VALUES ({}, {}, ' \
                        '"{}", "{}", "{}");'.format(candidate_index, constituency_index,
                        cname, cparty, ccoalition)
                print 'INSERT INTO result (constituency_id, candidate_id, votes, ' \
                        'votes_p, winner, majority) VALUES ' \
                        '({}, {}, {}, {}, {}, {});'.format(constituency_index,
                        candidate_index, opponent_votes, opponent_votes_p, 0, 0)
                candidate_index += 1

                gps = get_gps(constituency_name)
                #gps = {'lat': 0.1, 'lng': 0.2}
                print 'INSERT INTO constituency (id, code, name, state_id, ' \
                        'incumbent, eligible_voters, malay_voters, chinese_voters,' \
                        ' indian_voters, others_voters, muslim_bumi_voters, ' \
                        'non_muslim_bumi_voters, latitude, longitude) VALUES (' \
                        '{}, "{}", "{}", {}, "{}", {}, {}, {}, {}, {}, ' \
                        '{}, {}, {}, {});'.format(constituency_index,
                        constituency_code, constituency_name, state_index - 1,
                        incumbent, eligible_voters, malay_voters, chinese_voters,
                        indian_voters, others_voters, muslim_bumi_voters,
                        non_muslim_bumi_voters, gps['lat'], gps['lng'])

                print 'INSERT INTO stat (constituency_id, voter_turnout, ' \
                        'voter_turnout_p, spoilt_votes, spoilt_votes_p) ' \
                        'VALUES ({}, {}, {}, {}, {});'.format(constituency_index,
                        voter_turnout, voter_turnout_p, spoilt_votes,
                        spoilt_votes_p)

                constituency_index += 1

            count += 1
            ''' end of for line in f: '''


if __name__ == '__main__':
    main()
