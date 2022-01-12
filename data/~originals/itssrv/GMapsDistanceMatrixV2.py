################################################################################
import requests
from datetime import datetime
import time
import numpy as np
import sys
################################################################################
def print_out(file, text):
    file.write(text + '\n')
    file.flush()
##    print(text)
##    sys.stdout.flush()

class GMapsDistanceMatrix:
    def __init__(self, apikey):
        self.__apikey = apikey
    def get(self,origins,destinations, distance):
        tvalue = -1
        dvalue = -1
        res = requests.get(
            'https://maps.googleapis.com/maps/api/directions/json',
            params={
                'units': 'imperial',
                'departure_time': 'now',
                'origin': origins,
                'destination': destinations,
                'key': self.__apikey,
                'alternatives': 'true' 
                },
            timeout=3,
            )
        if res.status_code == 200: # OK
            json = res.json()
            # find time for all distance closest to distance
            if len(json['routes']) > 1:
                distanceMat = np.zeros(len(json['routes']))
                for i in range(len(json['routes'])):
                    distanceMat[i] = json['routes'][i]['legs'][0]['distance']['value']
                tvalue = json['routes'][np.argmin(abs(distanceMat - distance))]['legs'][0]['duration_in_traffic']['value']
                dvalue = json['routes'][np.argmin(abs(distanceMat - distance))]['legs'][0]['distance']['value']
            else:
                tvalue = json['routes'][0]['legs'][0]['duration_in_traffic']['value']
                dvalue = json['routes'][0]['legs'][0]['distance']['value']
        return tvalue, dvalue
################################################################################
if __name__ == "__main__":
    H1 = 'Cesar E. Chavez Memorial, 3746 University Ave, Riverside, CA 92501';
    H2 = '2980 University Ave, Riverside, CA 92507';
    H3 = '2460 University Ave, Riverside, CA 92507';    
    H4 = 'University FS Ottawa, Riverside, CA 92507';
    H4_2 = '1889 University Ave ste 109, Riverside, CA 92507';
    H5 = '1426 University Ave, Riverside, CA 92507';
    H6 = '948 University Ave, Riverside, CA 92507';

    F1 = '888 Martin Luther King Blvd, Riverside, CA 92507';
    F2 = 'ARCO, 1360 W Blaine St, Riverside, CA 92507';
    F3 = '3219 Spruce St, Riverside, CA 92501';
    F4 = 'Subway, 3315 14th St, Riverside, CA 92501';

    HWE_W = [H1, H2, H3, H4, H5]
    HWE_E = [H2, H3, H4, H5, H6]
    HEW_E = [H6, H5, H4_2, H3, H2]
    HEW_W = [H5, H4_2, H3, H2, H1]
    DistHEW = [836, 894, 829, 490, 929]    
    DistHWE = [931, 491, 808, 919, 837]
    DistFEW = [2327, 2514]
    DistFWE = [2974, 2449]
    # print(HWE_W)
    FEW_E = [F1, F3];
    FEW_W = [F2, F4];
    FWE_W = [F4, F2];
    FWE_E = [F3, F1];

    distancematrix = GMapsDistanceMatrix("AIzaSyAjP0WXTkWYpyd1rlcy3-xEJQZ3W2Uexbo")

    Data_log = open('C:/Projects/Zhensong/RiversideTravelTimeCollection{}.txt'.format(str(datetime.now().month)+'_'+str(datetime.now().day)+'_'+str(datetime.now().hour)+'_'+str(datetime.now().minute)), 'w')    
    while 1:
        c = datetime.now().minute
        if c%15 == 0:
            tTotal = []
            dTotal = []
            for i in range(5):
                origins = HEW_E[i]
                destinations = HEW_W[i]
                tvalue, dvalue = distancematrix.get(origins,destinations, DistHEW[i])
                tTotal.append(tvalue)
                dTotal.append(dvalue)
            for i in range(5):
                origins = HWE_W[i]
                destinations = HWE_E[i]
                tvalue, dvalue = distancematrix.get(origins,destinations, DistHWE[i])
                tTotal.append(tvalue)
                dTotal.append(dvalue)                
            for i in range(2):
                origins = FEW_E[i]
                destinations = FEW_W[i]
                tvalue, dvalue = distancematrix.get(origins,destinations, DistFEW[i])
                tTotal.append(tvalue)
                dTotal.append(dvalue)
            for i in range(2):
                origins = FWE_W[i]
                destinations = FWE_E[i]
                tvalue, dvalue = distancematrix.get(origins,destinations, DistFWE[i])
                tTotal.append(tvalue)
                dTotal.append(dvalue)                 
            format_str = ('time: %s  DisHEW1: %d TraHEW1: %d DisHEW2: %d TraHEW2: %d DisHEW3: %d TraHEW3: %d DisHEW4: %d TraHEW4: %d DisHEW5: %d TraHEW5: %d ') + \
                                   ('DisHWE1: %d TraHWE1: %d DisHWE2: %d TraHWE2: %d DisHWE3: %d TraHWE3: %d DisHWE4: %d TraHWE4: %d DisHWE5: %d TraHWE5: %d ') + \
                                   ('DisFEW1: %d TraFEW1: %d DisFEW2: %d TraFEW2: %d ') + \
                                   ('DisFWE1: %d TraFWE1: %d DisFWE2: %d TraFWE2: %d')
            text = (format_str % (datetime.now(), dTotal[0], tTotal[0], dTotal[1], tTotal[1], dTotal[2], tTotal[2], dTotal[3], tTotal[3], dTotal[4], tTotal[4], \
                                                  dTotal[5], tTotal[5], dTotal[6], tTotal[6], dTotal[7], tTotal[7], dTotal[8], tTotal[8], dTotal[9], tTotal[9], \
                                                  dTotal[10], tTotal[10], dTotal[11], tTotal[11], \
                                                  dTotal[12], tTotal[12], dTotal[13], tTotal[13]))
            print_out(Data_log, text)            
            time.sleep(800)
        time.sleep(1)
    

################################################################################
