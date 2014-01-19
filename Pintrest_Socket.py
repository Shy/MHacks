#!/usr/bin/python2

from pinterest.client import raw_client
from pinterest.client import ApiError
import json
from random import choice
from random import randint
import time
from datetime import datetime

class Pintrest_Socket(object):
    def __init__(self):
        self.APP_ID = "1435585"
        self.APP_SECRET = "721b878beede8ced1d3441e550841c85dbe65261"
        self.pin_client = raw_client(self.APP_ID, self.APP_SECRET)

    def find_pins(self, user_name):

        # Grab user boards
        user_boards_response = ""
        follow_boards_response = ""
        try:
            user_boards_response = self.pin_client.users(user_name).boards.get()
            follow_boards_response = self.pin_client.users(user_name).boards.following.get()
        except ApiError, e:
            # Something went wrong on the way to the Pinterest
            print 'Code:', e.code
            print 'Message:', e.message
            print 'Detail:', e.detail
            return None, None, None

        boards = user_boards_response[0] + follow_boards_response[0]

        while len(boards) != 0:
            chosen_board = choice(boards)

            postcard_type = randint(1, 5)
            pins = []
            if postcard_type <= 3:
                # 60% chance to grab from chosen board
                pins = self.__grab_pins(chosen_board)

            elif postcard_type == 4:
                # 20% chance to grab from contributor's board
                #TODO: change chosen board to contributor's board
                pins = self.__grab_pins(chosen_board)

            elif postcard_type == 5:
                # 20% chance to grab form a related board
                #TODO: change chosen board to a related board
                pins = self.__grab_pins(chosen_board)

            if len(pins):
                # Return top pin
                top_pin = pins[0]
                domain = None
                try:
                    domain = self.pin_client.domains(top_pin['domain']).get()
                except ApiError, e:
                    # Ignore this error for now. We are probably not using the domain
                    pass
                return pins[0], chosen_board, domain
            # No pins found. Remove board if postcard_type 1-3 and loop
            if postcard_type <= 3:
                boards.remove(chosen_board)
        raise Exception("No valid pins for given user.")

    def __convert_time(self, pin):
        """
        Convert from Pinterest's time format to time_struct
        """
        return time.strptime(pin['created_at'], "%a, %d %b %Y %H:%M:%S +0000")

    def __filter_pin_date(self, pin):
        """
        Make sure this pin was posted in the last month
        """
        pin_time = self.__convert_time(pin)
        now_time = datetime.now()
        cutoff_time = None
        if now_time.month == 1:
            cutoff_time = datetime(now_time.year-1, 12, now_time.day)
        else:
            cutoff_time = datetime(now_time.year, now_time.month-1, now_time.day)
        if pin_time >= time.mktime(cutoff_time.timetuple()):
            # Pin was posted after cutoff date
            return 1
        # Pin was posted before the cutoff date
        return 0

    def __filter_pin_size(self, pin):
        """
        Make sure this pin has a picture with an appropriate size
        """
        pin_size = pin['image_large_size_pixels']
        if ((pin_size['width'] >= 600 and pin_size['height'] >= 400) or
            (pin_size['width'] >= 400 and pin_size['height'] >= 600)):
            # Pin picture is large enough
            return 1
        # Pin picture is not large enough
        return 0

    def __grab_pins(self, board):
        """
        Grab pins from the last month
        """
        board_pins = []
        try:
            # Keep track of page place of pins
            bookmark = None
            # Go for a maximum of 10 pages worth of pins
            num_calls = 0
            while num_calls < 10:
                if bookmark == None:
                    board_pin_response = self.pin_client.boards(board['id']).pins.get()
                else:
                    board_pin_response = self.pin_client.boards(board['id']).pins.get(bookmark=bookmark)
                # Sort based on time
                sorted_pins = sorted(board_pin_response[0],
                                     key=self.__convert_time)
                # Filter based on date
                date_filtered_pins = filter(self.__filter_pin_date, sorted_pins)
                # Filter based on size
                size_filtered_pins = filter(self.__filter_pin_date, date_filtered_pins)

                board_pins += size_filtered_pins

                # Keep track of next bookmark
                bookmark = board_pin_response[1]

                if len(sorted_pins) != len(date_filtered_pins) or bookmark == None:
                    # Kill loop if no more pins, or out of month range
                    num_calls = 10
                else:
                    # Otherwise iterate
                    num_calls += 1
        except ApiError, e:
            print 'Code:', e.code
            print 'Message:', e.message
            print 'Detail:', e.detail
            raise
        # Sort based on like count (reversed so top is first)
        return sorted(board_pins, key=lambda x: x['like_count'], reverse=1)


def Get(user_name):
    client = Pintrest_Socket()
    top_pin, board, domain = client.find_pins(user_name)
    # print '\n\nTop Pin:\n\n', top_pin
    # print '\n\nBoard:\n\n', board
    # print '\n\nDomain:\n\n', domain
    return top_pin