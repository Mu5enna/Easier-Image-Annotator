import json
from typing import List, Dict
from zoneinfo import available_timezones


class JsonData:
    def __init__(self, box: List[float], class_id: float, track_id: float):
        self.box = box
        self.class_id = class_id
        self.track_id = track_id

    def dict_convert(self):
        return{
            "box": self.box,
            "class_id": self.class_id,
            "track_id": self.track_id,
        }

    @staticmethod
    def json_load(path):
        with open(path, "r") as json_file:
            data = json.load(json_file)
            return {k: JsonData(box=v["box"], class_id=v["class"], track_id=v["track_id"]) for k, v in data.items()}

    @staticmethod
    def json_dump(path, data: dict):
        serialized = {k:{"box": v.box, "class": v.class_id, "track_id": v.track_id,} if isinstance(v, JsonData) else v for k,v in data.items()}
        with open(path, "w") as json_file:
            json.dump(serialized, json_file, indent=4)

class Calculations:

    @staticmethod
    def available_box_id(json_object: Dict[str, JsonData]) -> int:

        box_ids: List[int] = []

        for key in json_object.keys():
            box_ids.append(int(key))

        if len(box_ids) == 0: return 0
        else: return max(box_ids) + 1


    @staticmethod
    def calc_diffs(add1: str, add2: str, track_ids: List[float]) -> List[List[float]]:

        matched_diffs = []

        json_object1 = JsonData.json_load(add1)
        json_object2 = JsonData.json_load(add2)

        for entry1 in json_object1.values():

            if entry1.track_id == 0 or not float(entry1.track_id) in track_ids: continue

            for entry2 in json_object2.values():

                if entry2.track_id == 0: continue

                if entry1.track_id == entry2.track_id:
                    diff_arry = [0.0] * 5
                    diff_arry[4] = entry1.track_id

                    for i in range(4):
                        diff_arry[i] = entry2.box[i] - entry1.box[i]

                    matched_diffs.append(diff_arry)

        return matched_diffs

    @staticmethod
    def calc_pi(coor_diffs: List[List[float]], img_diffs: int) -> List[List[float]]:

        list_pi: List[List[float]] = []

        for i in range(len(coor_diffs)):
            point_incr: List[float] = [0.0] * 5
            point_incr[4] = coor_diffs[i][4]
            for j in range(4):
                point_incr[j] = coor_diffs[i][j] / img_diffs
            list_pi.append(point_incr)

        return list_pi


    @staticmethod
    def calc_new_points(prev_addr: str, curr_addr: str, calc_pi: List[List[float]]):

        prev_json_object = JsonData.json_load(prev_addr)
        curr_json_object = JsonData.json_load(curr_addr)

        for i in range(len(calc_pi)):
            for entry_prev in prev_json_object.values():
                if entry_prev.track_id == calc_pi[i][4]:
                    does_contains = False
                    box_values = [float(entry_prev.box[0] + calc_pi[i][0]), float(entry_prev.box[1] + calc_pi[i][1]), float(entry_prev.box[2] + calc_pi[i][2]), float(entry_prev.box[3] + calc_pi[i][3])]
                    box_id = Calculations.available_box_id(curr_json_object)
                    for key, entry_curr in curr_json_object.items():
                        entry_curr = JsonData(box=entry_curr["box"], class_id=entry_curr["class"], track_id=entry_curr["track_id"])
                        if entry_curr.track_id == calc_pi[i][4]:
                            does_contains = True
                            box_id = int(key)
                            entry_curr.box = box_values
                            entry_curr.class_id = entry_prev.class_id

                    if not does_contains:
                        curr_json_object[box_id] = {
                            'box': box_values,
                            'class': entry_prev.class_id,
                            'track_id': entry_prev.track_id,
                        }

        JsonData.json_dump(curr_addr, curr_json_object)



file1_path = r"C:\Users\Eren\Desktop\00001.json"
file2_path = r"C:\Users\Eren\Desktop\00002.json"
file3_path = r"C:\Users\Eren\Desktop\00003.json"
track_id_list = [0,1,2]

print(Calculations.calc_new_points(file1_path, file2_path, Calculations.calc_pi(Calculations.calc_diffs(file1_path, file3_path, track_id_list), 2)))