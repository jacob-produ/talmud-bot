COURSE_TYPE_MAP = {
    700: "בוקר (700)",
    708: "בוקר (708)",
    720: "צהריים (720)",
    728: "צהריים (728)",
    300: "יום מלא",
    600: "בוקר וצהריים (600)",
    605: "בוקר וצהריים (605)",
    500: "ערב"
}

MULTIPLE_DAY_PART_COURSES = [600, 605]
COURSE_TYPE_REVERSED_MAP = {v: k for k, v in COURSE_TYPE_MAP.items()}

COURSE_TYPE_DAY_PART_MAP = {
    700: ["בוקר"],
    708: ["בוקר"],
    720: ["צהריים"],
    728: ["צהריים"],
    300: ["יום מלא"],
    600: ["בוקר", "צהריים"],
    605: ["בוקר", "צהריים"],
    500: ["ערב"]
}

COURSE_TYPE_DAY_PART_MAP_REVERSED = {}
for course_type, day_part_list in COURSE_TYPE_DAY_PART_MAP.items():
    for day_part in day_part_list:
        if day_part not in COURSE_TYPE_DAY_PART_MAP_REVERSED:
            COURSE_TYPE_DAY_PART_MAP_REVERSED[day_part] = []
        COURSE_TYPE_DAY_PART_MAP_REVERSED[day_part].append(course_type)


def get_course_types_converted_list(course_types):
    return [COURSE_TYPE_REVERSED_MAP[c_t] for c_t in course_types if c_t in COURSE_TYPE_REVERSED_MAP.keys()]


# TEST
if __name__ == "__main__":
    print(COURSE_TYPE_DAY_PART_MAP_REVERSED.keys())
