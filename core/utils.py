import pandas as pd
import zipfile, os, inspect, importlib
from configparser import ConfigParser


def write_to_file(file_name, data_list, prefix='', suffix=''):
    with open(file_name, 'w') as f:
        f.write(f'{prefix} \n')
        for line in data_list:
            f.write(f'{line} \n')
        f.write(suffix)


def dfs_to_excel(df_list, sheet_list, file_name='tables_excel.xlsx'):
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    for df, sheet in zip(df_list, sheet_list):
        df.to_excel(writer, sheet_name=sheet, startrow=0, startcol=0, index=False)
    writer.save()


def compress_files_to_zip(files_to_compress, zip_file_name):
    with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
        for file in files_to_compress:
            zip_file.write(file, os.path.basename(file))

    with open(zip_file_name, 'rb') as zip_file:
        data = zip_file.readlines()
    return data


def get_python_file_from_dir(path):
    ofs_package_files = os.listdir(path)
    file_names_paths = {}
    for file in ofs_package_files:
        file_name = os.path.basename(file).split(".")
        if len(file_name) != 2 or file_name[1] != "py" or file_name[0] in ['__init__']:
            continue
        file_names_paths[file_name[0]] = file
    return file_names_paths


def import_class_from_file(files_to_import=[]):
    modules_classes = []
    for class_name, file_path in files_to_import:
        for name, clss in inspect.getmembers(importlib.import_module(file_path), inspect.isclass):
            if name.lower() == class_name.lower():
                modules_classes.append(clss)
    return modules_classes


def read_config_file(config_file_path):
    print(config_file_path)
    config = ConfigParser()
    try:
        config.read(config_file_path)
    except Exception as e:
        raise Exception(f"Could not open config file: {e}")
    return config


def convert_csv_row_empty_string_to_none(csv_row: dict):
    return {key.strip(): (val if val != '' else None) for key, val in csv_row.items()}


def convert_str_to_int(int_str):
    try:
        return int(int_str)
    except ValueError as e:
        return None


def convert_str_to_float(float_str):
    try:
        return float(float_str)
    except ValueError as e:
        return None



def convert_str_to_datetime(date_str):
    import dateparser
    return dateparser.parse(date_str, date_formats=['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%d/%m/%YT%H:%M:%S'],
                            settings={'DATE_ORDER': 'YMD', 'PREFER_DAY_OF_MONTH': 'first', 'TIMEZONE': '+0200'})


def convert_csv_row_dtype(csv_row: dict, col_dtypes_map: dict):
    converted_row = {}
    for col_name, col_val in csv_row.items():
        if col_val is None or col_name not in col_dtypes_map:
            converted_row[col_name] = col_val
            continue
        col_val = col_val.strip()
        if col_dtypes_map[col_name] == "int":
            converted_val = convert_str_to_int(col_val)
        elif col_dtypes_map[col_name] == "float":
            converted_val = convert_str_to_float(col_val)
        elif col_dtypes_map[col_name] == "date":
            converted_val = convert_str_to_datetime(col_val).isoformat()
        else:
            converted_val = col_val
        converted_row[col_name] = converted_val
    return converted_row


def create_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False

