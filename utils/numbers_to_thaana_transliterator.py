from typing import List


def _multiple_explode(delimiters, string):
    return string.replace(delimiters, chr(1)).split(chr(1))


def sub_divide_numbers_into_places(number: str) -> List[List[str]]:
    reversed_number = number[::-1]
    result = []
    i = 0
    while i < len(reversed_number):
        tmp_array = ['', '']
        if i + 2 < len(reversed_number):
            tmp_array[0] = reversed_number[i + 2]
        else:
            tmp_array[0] = ""
        if i + 1 < len(reversed_number):
            tmp_array[1] = reversed_number[i + 1] + reversed_number[i]
        else:
            tmp_array[1] = reversed_number[i]
        result.append(tmp_array)
        i += 3
    return result[::-1]


def get_number_of_places(number_array: list) -> int:
    number_of_places = 0
    for combo in number_array:
        for elem in combo:
            if elem != "":
                number_of_places += 1
    return number_of_places


class NumbersToThaanaTransliterator:

    place_values_mappings = {
        0: '',
        1: '',
        2: 'ސަތޭކަ',
        3: 'ހާސް',
        4: 'ލައްކަ',
        5: 'މިލިޔަން',
        6: 'މިލިޔަން',
        7: 'މިލިޔަން',
        8: 'މިލިޔަން',
        9: 'ބިލިޔަން'
    }

    triple_digit_mappings = {
        '00': '',
        '0': '',
        '1': 'އެއް',
        '01': 'އެއް',
        '2': 'ދެ',
        '02': 'ދެ',
        '3': 'ތިން',
        '03': 'ތިން',
        '4': 'ހަތަރު',
        '04': 'ހަތަރު',
        '5': 'ފަސް',
        '05': 'ފަސް',
        '6': 'ހަ',
        '06': 'ހަ',
        '7': 'ހަތް',
        '07': 'ހަތް',
        '8': 'އަށް',
        '08': 'އަށް',
        '9': 'ނުވަ',
        '09': 'ނުވަ',
        '10': 'ދިހަ',
        '11': 'އެގާރަ',
        '12': 'ބާރަ',
        '13': 'ތޭރަ',
        '14': 'ސާދަ',
        '15': 'ފަނަރަ',
        '16': 'ސޯޅަ',
        '17': 'ސަތާރަ',
        '18': 'އަށާރަ',
        '19': 'އޮނަވިހި',
        '20': 'ވިހި',
        '21': 'އެކާވީސް',
        '22': 'ބާވީސް',
        '23': 'ތޭވީސް',
        '24': 'ސައުއްވީސް',
        '25': 'ފަންސަވީސް',
        '26': 'ސައްބީސް',
        '27': 'ހަތާވީސް',
        '28': 'އަށާވީސް',
        '29': 'އޮނަތިރީސް',
        '30': 'ތިރީސް',
        '31': 'އެއްތިރީސް',
        '32': 'ބައްތިރީސް',
        '33': 'ތެއްތިރީސް',
        '40': 'ސާޅީސް',
        '50': 'ފަންސާސް',
        '60': 'ފަސްދޮޅަސް',
        '70': 'ހަތްދިހަ',
        '80': 'އަށްޑިހަ',
        '90': 'ނުވަދިހަ',
        '100': 'ސަތޭކަ',
        '200': 'ދުއިސައްތަ'
    }

    def __init__(self):
        pass


    def transliterate(self, number: str) -> str:
        number_array = self.convert_number_array_to_language(sub_divide_numbers_into_places(number))
        return ' '.join(number_array)


    def pre_process_tens(self, number: str, mode: str = 'mid') -> str:
        result = []
        if len(number) == 2:
            tens_place_number = number[0]
            ones_place_number = number[1]
            if int(number) > 33 and ones_place_number != '0':
                tens_place_index = tens_place_number + '0'
                if tens_place_index in self.triple_digit_mappings:
                    result.append(self.triple_digit_mappings[tens_place_index])
                if mode == 'mid':
                    if ones_place_number in self.triple_digit_mappings:
                        result.append(self.triple_digit_mappings[ones_place_number])
                elif mode == 'end':
                    if ones_place_number in self.single_digit_mappings:
                        result.append(self.single_digit_mappings[ones_place_number])
                return ' '.join(result)
            else:
                if number in self.triple_digit_mappings:
                    return self.triple_digit_mappings[number]
                else:
                    return ''
        else:
            if mode == 'mid':
                if number in self.triple_digit_mappings:
                    result.append(self.triple_digit_mappings[number])
            elif mode == 'end':
                if number in self.triple_digit_mappings:
                    result.append(self.single_digit_mappings[number])
            return ' '.join(result)

    def convert_number_array_to_language(self, number_array: list) -> list:
        place_number = get_number_of_places(number_array)
        result = []
        for i in range(len(number_array)):
            language_value = ''
            number_grouping = number_array[i]
            if number_grouping[0] != "":
                if number_grouping[0] in self.triple_digit_mappings:
                    language_value = self.triple_digit_mappings[number_grouping[0]]
                    language_value += self.place_values_mappings[place_number]
                    if language_value == 'ދެސަތޭކަ':
                        language_value = 'ދުއިސައްތަ'
                    place_number -= 1
                else:
                    continue
            language_value += self.pre_process_tens(number_grouping[1])
            language_value += self.place_values_mappings[place_number]
            result.append(language_value)
            place_number -= 1
        return result
