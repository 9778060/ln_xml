from bigxml import Parser, xml_handle_element, xml_handle_text
from collections import defaultdict
import re
import pandas as pd
import os

FOLDER_NAME = "data"
FILE_EXT_IN = "xml"
FILE_EXT_OUT = "csv"

# FILE_NAME = "1st_Export_Xml_Report"
# FILE_NAME = "2nd_Export_Xml_Report"
# FILE_NAME = "3rd_Export_Xml_Report"
# FILE_NAME = "4th_Export_Xml_Report"
FILE_NAME = "test"

record_counter = 0


def _get_group_id_from_notes(input_str):
    if match := re.search(r'Group ID:[\s]*(\d+)[.]*$', input_str):
        return match.groups()[0]



@xml_handle_element("ResultRecords", "ResultRecord")
class Record:
    
    def __init__(self, node):
        global record_counter

        record_counter += 1
        self.id = record_counter


    @xml_handle_element("WatchListResult", "Matches", "Match", "Notes")
    def handle_notes(self, node):
        yield {"notes": _get_group_id_from_notes(node.text)}


    def xml_handler(self, items):
        # yield f"START cart parsing for id {self.id}"
        yield from items
        # yield dict((key, d[key]) for d in list(items) for key in d)
        yield f"Parsed record id {self.id}"


def main():
    with open(os.path.join(FOLDER_NAME, FILE_NAME) + os.extsep + FILE_EXT_IN, "rb") as stream:
        list_of_dicts = []
        for item in Parser(stream).iter_from(Record):
            if isinstance(item, dict):
                list_of_dicts.append(item)
            else:
                print(item)


    df = pd.DataFrame.from_dict(list_of_dicts)

    df.to_csv(os.path.join(FOLDER_NAME, FILE_NAME) + "_notes_regexp" + os.extsep + FILE_EXT_OUT, index=False)

if __name__ == "__main__":
    main()