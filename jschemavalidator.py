from os import listdir, path
from json import load
from datetime import datetime as dt

from jsonschema import Draft7Validator
JSON_DIR = 'event'
SCHEMA_DIR = 'schema'

VALUE_VALIDATOR = {
    'type': "измените ожидаемый тип данных в схеме или передавайте ожидаемый тип",
    'required': "необходимо передавать значение или убрать его из требуемых. Возможно неверная схема"
}


def get_event(json_path):
    with open(json_path, 'r') as jsonfile:
        json = load(jsonfile)
        evnt = json.get('event') if json else None
    return evnt


def val_json(scheme_path, json_path):
    log_data = ""
    valid_scheme = ""
    with open(scheme_path, 'r') as sch:
        schema = load(sch)

    with open(json_path, 'r') as inst:
        instance = load(inst)

    instance = instance.get('data') if instance else None

    try:
        v = Draft7Validator(schema)
        errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
        if errors:
            for ex in errors:
                exceptpath = 'path: ' + ex.path.popleft() if len(ex.path) else ""
                print(f"ошибка {ex.message} при проверке параметра '{ex.validator}' {exceptpath}")
                log_data += f"ошибка {ex.message} при проверке параметра '{ex.validator}' {exceptpath}\n"
                if ex.validator in VALUE_VALIDATOR:
                    print(f'{VALUE_VALIDATOR[ex.validator]}')
                    log_data += f'{VALUE_VALIDATOR[ex.validator]}\n'
        else:
            print('valid')
            log_data += f'valid\n'
            valid_scheme = schema
    except Exception as ex:
        print(ex)
    return valid_scheme, log_data


def json_file_list(dirpath, extension):
    filelist = []
    try:
        for i in listdir(dirpath):
            # print(f'i {i}')
            _, ext = path.splitext(i)
            # print(f'ext {ext}')
            if ext == extension:
                filelist.append(i)
    except FileNotFoundError as ex:
        print(f'File not found {ex.filename}')
    # print(f'filelist {extension} {filelist}')
    return filelist


def base(logfile):

    filelist = json_file_list(JSON_DIR, '.json')
    schlist = json_file_list(SCHEMA_DIR, '.schema')

    if not filelist or not schlist:
        logfile.write(f"file(s) not found\n")
        return 0

    # active_scheme = schlist[int(sys.argv[1])]
    validation_result = []
    # print(schlist)
    for iter_json in filelist:

        event_category = get_event(path.join(JSON_DIR, iter_json))
        print(f'\n{iter_json} event: {event_category}')
        logfile.write(f'\n{iter_json} event: {event_category}\n')
        for iter_scheme in schlist:
            print(f'{iter_scheme}:')
            logfile.write(f'{iter_scheme}:\n')
            rez, log_data = val_json(path.join(SCHEMA_DIR, iter_scheme), path.join(JSON_DIR, iter_json))
            logfile.write(f'{log_data}\n')
            if rez:
                validation_result.append([iter_scheme, iter_json])

    print(f'\nVALIDATION SUCCESS RESULT:\n{validation_result}\n')
    logfile.write(f'\nVALIDATION SUCCESS RESULT:\n{validation_result}\n')


if __name__ == '__main__':
    print(100*"*")
    with open('log.txt', 'a') as log:
        log.write(str(dt.now()))
        base(log)
    log.close()
