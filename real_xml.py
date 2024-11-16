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
match_counter = 0


def _get_group_id_from_notes(input_str):
    if match := re.search(r'Group ID:[\s]*(\d+)[.]*$', input_str):
        return match.groups()[0]


@xml_handle_element("Match")
class Matches:
    def __init__(self):
        global match_counter

        match_counter += 1
        self.match_counter = match_counter
        

    @xml_handle_element("Score")
    def handle_score(self, node):
        yield {self.match_counter: {"match_score": node.text}}


    @xml_handle_element("Id")
    def handle_id(self, node):
        yield {self.match_counter: {"match_id": node.text}}


    @xml_handle_element("Name", "Full")
    def handle_full_name(self, node):
        yield {self.match_counter: {"match_full_name": node.text}}


    @xml_handle_element("Notes")
    def handle_group_id(self, node):
        group_id = _get_group_id_from_notes(node.text)
        yield {self.match_counter: {"match_group_id": group_id}}


    @xml_handle_element("Number")
    def handle_number(self, node):
        yield {self.match_counter: {"match_number": node.text}}


    def xml_handler(self, items):
        yield from items



@xml_handle_element("ResultRecords", "ResultRecord")
class Record:
    
    def __init__(self, node):
        global record_counter

        record_counter += 1
        self.id = record_counter


    @xml_handle_element("Id")
    def handle_id(self, node):
        yield {"id": node.text}


    @xml_handle_element("InputEntity", "Account", "Number")
    def handle_account_number(self, node):
        yield {"account_number": node.text}


    @xml_handle_element("InputEntity", "Name", "Full")
    def handle_full_name(self, node):
        yield {"full_name": node.text}


    @xml_handle_element("WatchListResult", "Matches")
    def handle_matches(self, node):
        dd = defaultdict(list)
        for match in node.iter_from(Matches):
            for k, v in match.items():
                dd[k].append(v)
            
        new_list = []
        for k, v in dd.items():
            new_list.append(dict((key, d[key]) for d in v for key in d))
            
        yield {"matches": new_list}


    def xml_handler(self, items):
        # yield f"START cart parsing for id {self.id}"
        yield dict((key, d[key]) for d in list(items) for key in d)
        yield f"Parsed record id {self.id}"


def main():
    with open(os.path.join(FOLDER_NAME, FILE_NAME) + os.extsep + FILE_EXT_IN, "rb") as stream:
        list_of_dicts = []
        for item in Parser(stream).iter_from(Record):
            if isinstance(item, dict):
                list_of_dicts.append(item)
            else:
                print(item)

    new_list = []

    for item in list_of_dicts:
        new_item = item.copy()
        del new_item["matches"]

        if item.get("matches", None):
            for match in item.get("matches", None):
                new_dict_item = {**new_item, **match}
                new_list.append(new_dict_item)
        else:
            new_list.append(new_item)

    df = pd.DataFrame.from_dict(new_list)

    df.to_csv(os.path.join(FOLDER_NAME, FILE_NAME) + os.extsep + FILE_EXT_OUT, index=False)

if __name__ == "__main__":
    main()