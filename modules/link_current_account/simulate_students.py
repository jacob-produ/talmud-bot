import random,os

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CHECK_ASSETS_PATH = os.path.join(DIR_PATH,'assets/check')

def random_digits(digits_len):
    lower_bound = 10**(digits_len-1)
    upper_bound = 10**digits_len - 1
    return lower_bound, upper_bound

def simulate_students(num_of_rec=40000, id_len=9):
    try:
        with open(os.path.join(DIR_PATH,'first_names.txt'), 'r', encoding='utf-8') as first_names_file, \
                open(os.path.join(DIR_PATH,'last_names.txt'), 'r', encoding='utf-8') as last_name_file:
            first_names,last_names = first_names_file.read().splitlines(), last_name_file.read().splitlines()
        id_lower_bound, id_upper_bound = random_digits(id_len)
        return [{'identity':random.randint(id_lower_bound,id_upper_bound),
                 'first_name':random.choice(first_names), 'last_name':random.choice(last_names)}
                for i in range(num_of_rec)]
    except IOError as e:
        return None




if __name__ == '__main__':
    print(simulate_students())