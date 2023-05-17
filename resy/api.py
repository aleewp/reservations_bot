import os
import json
import datetime as dt

from typing import List
from base import BaseWrapper

RESY_API_KEY = os.getenv('RESY_API_KEY')

class ResyWrapper(BaseWrapper):
    
    def __init__(self, *args, **kwargs):
        super(ResyWrapper, self).__init__(*args, **kwargs)
        self.base_url = 'https://staging-api.resy.com/'
        self.headers = {'Authorization': f'ResyAPI api_key="{RESY_API_KEY}"',
                        'Content-Type': 'application/x-www-form-urlencoded'}
        
        # The email and password ofr an account are name mangled attributes
        # so they will not be accessible late and avoid any inherited conflicts
        self.__email = os.getenv('RESY_ACCOUNT_EMAIL')
        self.__password = os.getenv('RESY_ACCOUNT_PASSWORD')
        
    def _get_auth_token(self) -> str:
        '''
        Get the authorization token, required to make any reservation

        Returns
        -------
        auth_token : str
            The auth token which is required to make all requests for a given user
        '''
        auth_token = ''
        body = {'email': self.__email, 'password': self.__password}
        AUTH_URL = self.base_url + '/3/auth/mobile'
        resy_response = self.post(AUTH_URL, headers= self.headers, data=json.dumps(body))
        response = resy_response.json()
        if 'token' in resy_response:
            auth_token = response['token']
        assert len(auth_token) > 0, ('No auth token was generated with the provided email and password.'
                                     'Please check that they are correct and stored in the environment variables.')
        return auth_token
        
    def find_table(self, reservation_date:dt.datetime,  num_people:int, venue_id:int) -> List[str]:
        '''
        Find if there are any times available for a given restauraunt, time range, number of people
        
        Parameters
        ----------
        reservation_date : dt.datetime
            The beginning of the time range in question
        num_people : int
            How large the party for the reservation is
        venue_id : int
            The ID associated with the restauraunt in question

        Returns
        -------
        config_slots : List[str]
            This will return all of the config slots for a given day, times, table type
        '''
        params = {
            'venue_id' : venue_id,
            'num_people': num_people,
            'day' : reservation_date.strftime('%Y-%m-%d')
        }
        FIND_URL = self.base_url + '/4/find'
        availabilities = self.get(FIND_URL, headers=self.headers, params=params)
        response = availabilities.json()
        return [i['config'] for i in response['slots']]
    
    def make_reservation(self, reservation_date:dt.datetime,  num_people:int, config_id:str) -> bool:
        '''
        Make the reservation for a given configuartion id
        
        Parameters
        ----------
        reservation_date : dt.datetime
            The beginning of the time range in question
        num_people : int
            How large the party for the reservation is
        config_id : str
            The ID associated with the reservation trying to be made

        Returns
        -------
        successful : bool
            Was the reservation successfully made
        '''
        params = {
            'config_id' : config_id,
            'num_people': num_people,
            'day' : reservation_date.strftime('%Y-%m-%d')
        }
        RESERVATION_URL = self.base_url + '/3/details'
        reservation_details = self.get(RESERVATION_URL, headers=self.headers, params=params)
        book_token = reservation_details.json()['book_token']['value']
        auth_token = self._get_auth_token()
        BOOK_URL = self.base_url + '/3/book'
        # Note a new header is required to make the booking due to the authtoken and content type
        new_header = {
            'Authorization': f'ResyAPI api_key="{RESY_API_KEY}"',
            'X-Resy-Auth-Token': auth_token,
            'Content-Type': 'multipart/form-data'
        }
        booking_details = self.post(BOOK_URL, headers=new_header, data={'book_token': book_token})
        if booking_details.ok:
            return True
        else:
            return False

    
if __name__ == '__main__':
    resy_bot = ResyWrapper()
    resy_bot.make_reservation(dt.datetime.now(), 2, 'rgs://resy/2042632/108580/2/2019-06-23/2019-06-23/18:00:00/2/Dining%20Room')
    