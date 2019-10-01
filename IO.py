import csv
import re


def read_csv(file_path):
    # wczytanie plików csv
    with open(file_path, 'r', encoding='utf8') as file:
        reader = csv.reader(file, delimiter=',')
        return [row for row in reader]


def read_solution(file_path):
    # wczytanie pliku z rozwiązaniem
    with open(file_path, 'r') as file:
        data = file.read()
    route, profit, worked_time = data.split('\n')[:3]
    route = re.findall(r'\((.+?)\)', route)
    route = [city.replace('(', '').replace(')', '') for city in route]
    route = [city.split(',') for city in route]
    route = [[city_name, float(x), float(y), float(quantity)] for city_name, x, y, quantity in route]
    return route, float(profit), float(worked_time)


def save_solution(data, file_path):
    # zapisanie pliku z rozwiązaniem
    with open(file_path, 'w', newline='') as file:
        file.writelines(data)


def save_csv(data, file_path):
    # zapisanie csvki
    with open(file_path, 'w', encoding='utf8', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        for row in data:
            writer.writerow(row)
