import asyncio
import time
from core.data.dataclass import DataClass
from core.sources.forbes_scraper.forbes import ForbesVip
# from core.sources.celebrity_api.celebrity_api import CelebrityApi

# search_list = [
#     {
#     "name": "fola",
#     "age": 86,
#     "occupation": "influencer",
#     "email": "fkh@gmail.com",
#     "gender": "male"
# },

#   {
#     "name": "bolu",
#     "age": 86,
#     "occupation": "influencer",
#     "email": "fkh@gmail.com",
#     "gender": "male"
# },
# ]


class Process():
    """
    This Class Process the user input which can either be a dict  or a list

    Main Method: main()

    Args
        search_info (list) || (dict): VIP (celebrity) name to lookup.

    Return 
        List of List  || List of Dictionaries

    """

    def __init__(self, search_info):
        self.search_info = search_info

    async def main(self):
        """
        Main method 
        """
        try:
            if type(self.search_info) == list:
                response = []
                for info in self.search_info:
                    service_response = await self.get_service_response(info)
                    data_response = DataClass(service_response, **info)
                    result= data_response.initiate()
                    response.append(result)
            else:
                service_response = await self.get_service_response(self.search_info)
                data_response = DataClass(service_response, **self.search_info)
                response = data_response.initiate()
            return response
        except Exception as e:
            print(f"There was an error somewhere in the process class {e}")
            raise Exception

    async def runService(self, Service, info):
        response = Service().process(info)
        return response

    async def get_service_response(self, info):
        service1, service2 = await asyncio.gather(self.runService(ForbesVip, info), self.runService(ForbesVip, info))
        return [service1, service2]
