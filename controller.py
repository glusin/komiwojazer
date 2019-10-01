from _thread import start_new_thread
from queue import Queue

import IO
from algorithm import GeneticAlgorithm, Route
from gui import TravellingSalesmanApp


class Controller:
    def __init__(self):
        self.app = TravellingSalesmanApp()  # inicjalizacja okienka
        self.cities = None  # tu będzie lista miast
        self.connections = None  # tu będzie lista połączeń między miastami
        self.salesman_max_time = None  # tu będzie maksymalny czas pracy komiwojażera
        self.solution = None  # tu będzie zapisane rozwiązanie
        self.app.set_values_to_default(
            **GeneticAlgorithm.DEFAULT_SETTINGS)  # ustawienie domyślnych wartości hiperparametrów w okienku
        self.feedback_queue = Queue()  # tu będą zapisane akcje, które controller będzie chciał wykonać w okienku

    def mainloop(self):
        # metoda cały czas sprawdza akcje wykonane przez użytkownika i podejmuje odpowiednie działania w odpowiedzi
        # na nie a następnie odświeża okienko
        while self.app.is_alive:
            action = self.app.get_user_action()  # pobranie akcji użytkownika
            self.make_action(action)  # wykonanie akcji użytkownika
            self.make_feedback()  # jeżeli akcja użytkownika wymaga jakiejś akcji w okienku to tutaj zostanie to
            # wykonane
            self.app.refresh()  # odświeżenie okienka

    def make_action(self, action):
        # metoda sprawdza jaką akcję wykonał użytkownik i podejmuje odpowiednie działanie
        if not action:
            return

        # sprawdzenie typu akcji
        action_type = action['action']
        del action['action']
        if action_type == 'read_cities':
            func = self.read_cities

        elif action_type == 'read_connections':
            func = self.read_connections

        elif action_type == 'read_salesman_max_time':
            func = self.read_salesman_max_time

        elif action_type == 'find_solution':
            func = self.find_best_route

        elif action_type == 'save_solution':
            func = self.save_solution

        elif action_type == 'load_solution':
            func = self.read_route

        elif action_type == 'check_solution':
            func = self.check_solution
        elif action_type == 'show_map':
            func = self.show_map
        elif action_type == 'quit':
            func = self.quit
        else:
            self.error_message('Funkcja nie została jeszcze w pełni zaimplementowana')
            return

        # wykonanie odpowiedniej funkcji
        start_new_thread(func, (), action)
        # self.app.block_buttons()

    def read_cities(self, filename):
        # wczytanie danych miast z pliku filename
        try:
            # próba wczytania danych
            cities = IO.read_csv(filename)
            cities = [[city, float(x), float(y), float(profit)] for city, x, y, profit in cities]

        except Exception as e:
            # wyświetlenie informacji o błędzie w przypadku niepowodzenia
            self.error_message(f'Wystąpił nieoczekiwany błąd podczas wczytywania danych miast: {e}')
            return

        # mapa powinna zawierać co najmniej dwa miasta. Wyświetlenie błędu jeśli jest ich za mało
        if len(cities) < 2:
            self.error_message('Liczba miast powinna wynosić co najmniej 2.')
        else:
            self.cities = cities

    def read_connections(self, filename):
        if not self.cities:
            self.info_message('Wczytaj najpierw dane miast')
            return

        # wczytanie danych połączeń między miastami z pliku filename
        try:
            # próba wczytania danych
            connections = IO.read_csv(filename)
            connections = [[city1, city2, float(distance)] for city1, city2, distance in connections]
        except Exception as e:
            # wyświetlenie informacji o błędzie w przypadku niepowodzenia
            self.error_message(f'Wystąpił nieoczekiwany błąd podczas wczytywania połączeń: {e}')
            return

        # zapisanie trasy tylko jeśli okaże się poprawna
        if self.check_connections(connections):
            self.connections = connections

    def check_connections(self, connections):
        # liczba połączeń musi wynosić co najmniej 1. Wyświetlenie informacji o błędzie jeśli nie ma połączeń
        n_connections = sum([1 for c in connections if c])
        if n_connections == 0:
            self.error_message('Liczba połączeń powinna wynosić co najmniej 1.')
            return False

        # przygotowanie słownika miast
        city_name_to_coordinates = {city_name: (x, y) for city_name, x, y, profit in self.cities}

        for city1, city2, distance in connections:
            # odległość między miastami musi wynosić 1
            if distance != 1:
                self.info_message('Odległość między podanymi miastami jest różna od 1')

            x1, y1 = city_name_to_coordinates[city1]
            x2, y2 = city_name_to_coordinates[city2]
            dx = abs(x1 - x2)
            dy = abs(y1 - y2)
            # miasto może być połączone tylko z miastem bezpośrednio na lewo, prawo, górę lub dół
            if not ((dx, dy) == (1, 0) or (dx, dy) == (0, 1)):
                self.info_message(f'Miasta {city1} oraz {city2} nie mog być ze sobą połączone')
                return False

        return True

    def read_salesman_max_time(self, filename):
        # wczytanie danych czasu pracy komiwojażera z pliku filename
        try:
            # próba wczytania danych
            salesman_max_time = int(IO.read_csv(filename)[0][0])
        except ValueError as e:
            self.error_message(f'Czas pracy Komiwojażera musi być liczbą')
            return
        except Exception as e:
            # wyświetlenie informacji o błędzie w przypadku niepowodzenia
            self.error_message(f'Wystąpił nieoczekiwany błąd podczas wczytywania czasu pracy komiwojażera: {e}')
            return

        # czas pracy nie może być ujemny. Wyświetlenie informacji o błędzie jeśli jest ujemny
        if salesman_max_time <= 0:
            self.error_message('Czas podróży komiwojażera jest niepoprawny (mniejszy od 0). ')
        else:
            self.salesman_max_time = salesman_max_time

    def read_route(self, filename):
        # wczytanie rozwiązania z pliku
        try:
            route, profit, salesman_time = IO.read_solution(filename)
            print(route)
        except Exception as e:
            self.error_message(f'Wystąpił nieoczekiwany błąd podczas wczytywania trasy: {e}')
            return

        self.solution = route

    def find_best_route(self, **kwargs):
        # uruchomienie algorytmu szukającego optymalnej ścieżki
        if not self.cities or not self.connections or not self.salesman_max_time:
            self.info_message('Do uruchomienia algorytmu niezbędne są informacje o miastach, połączeniach między nimi '
                              'oraz czasie pracy komiwojażera')
            return
        # ponieważ często czas pracy algorytmu jest duży (liczony w sekundach) to blokowane są przyciski,
        # aby użytkownik nic nie zrobił
        self.block_buttons()
        try:
            # próba wyznaczenia optymalnej ścieżki
            algorithm = GeneticAlgorithm(self.cities, self.connections, self.salesman_max_time)
            print('#', self.connections)
            best_route = algorithm.find_optimal_route(**kwargs)  # zapisanie znalezionej ścieżki
            self.unblock_buttons()  # odblokowanie przycisków
            for city in best_route.route:
                print(city, best_route.cities[city].id)
            for city_coordinates in best_route.get_route_coordinates():
                print(city_coordinates)
        except Exception as e:
            # wyświetlenie informacji o błędzie podczas pracy algorytmu
            self.unblock_buttons()
            self.error_message(f'Wystąpił błąd podczas szukania optymalnej trasy: {e}')
            return

        self.solution = self.parse_route_for_solution(best_route)

    @staticmethod
    def parse_route_for_solution(route):
        # metoda zamienia wynik metody self.find_best_route do odpowiedniej postaci
        solution = []
        visited_cities = set()
        for city_name in route.route:
            x = route.cities[city_name].x
            y = route.cities[city_name].y
            profit = 0 if city_name in visited_cities else route.cities[city_name].profit

            solution.append([city_name, x, y, profit])
            visited_cities.add(city_name)
        return solution

    def save_solution(self, filename):
        # metoda zapisująca rozwiązanie do pliku filename jeśli rozwiązanie istnieje
        # w przeciwnym razie poinformowanie użytkownika, że rozwiązanie nie zostało wyznaczone lub wczytane
        if not self.solution:
            self.error_message('Brak rozwiązania, które można zapisać')
            return

        if not self.connections:
            self.error_message('W celu zapisania rozwiązania niezbędne są dane miast')
            return

        if not self.cities:
            self.error_message('W celu zapisania rozwiązania niezbędne są dane połączeń między miastami')
            return

        # przekształcenie do wymaganego formatu
        solution = [[str(element) for element in city] for city in self.solution]
        route_string = [','.join(city) for city in solution]
        route_string = [f'({city})' for city in route_string]
        route_string = ','.join(route_string)
        route_string = f'[{route_string}]'

        cities = GeneticAlgorithm.construct_cities(self.cities, self.connections)
        solution_cities = [city[0] for city in self.solution]  # wybieramy tylko id miast
        route = Route(solution_cities, cities)
        data = '\r\n'.join([route_string, str(route.fitness), str(route.distance)])

        # upewniamy się, że nazwa pliku, który zapisujemy ma rozszerzenie .txt i dodajemy jeśli nie ma
        if not filename.endswith('.txt'):
            filename += '.txt'
        IO.save_solution(data, filename)

    def block_buttons(self):
        # dodanie do kolejki zadań zablokowania przycisków okienka
        self.feedback_queue.put({'func': self.app.block_buttons})

    def unblock_buttons(self):
        # dodanie do kolejki zadań odblokowania przycisków okienka
        self.feedback_queue.put({'func': self.app.unblock_buttons})

    def error_message(self, message):
        # dodanie do kolejki zadań wyświetlenia informacji o błędzie
        self.feedback_queue.put({'func': self.app.error_message, 'message': message})

    def info_message(self, message):
        # dodanie do kolejki zadań wyświetlenia informacji
        self.feedback_queue.put({'func': self.app.info_message, 'message': message})

    def make_feedback(self):
        # wykonanie funkcji z kolejki jeśli kolejka nie jest pusta
        if not self.feedback_queue.empty():
            feedback = self.feedback_queue.get_nowait()
            self._execute_feedback(**feedback)

    def check_solution(self):
        # metoda sprawdzająca czy rozwiązanie jest prawidłowe
        if self.salesman_max_time is None:
            # wyświetlenie komunikatu o błędzie jeśli czas pracy komiwojażera nie został wczytany
            self.info_message('Wczytaj najpierw czas pracy Komiwojażera')
            return

        if not self.solution:
            # wyświetlenie komunikatu o błędzie jeśli rozwiązanie nie zostało wczytane lub wyznaczone
            self.error_message('Brak wczytanego lub obliczonego rozwiązania')
            return

        if not self.cities or not self.connections:
            # do weryfikacji poprawności trasy potrzebujemy listy miast i połączeń między nimi
            self.info_message('Do weryfikacji poprawności trasy niezbędne są: lista miast oraz połączeń między nimi')
            return

        # przekształcamy trasę rozwiązania do postaci obiektu Route
        cities = GeneticAlgorithm.construct_cities(self.cities, self.connections)  # najpierw tworzymy miasta
        solution_cities = [city[0] for city in self.solution]  # wybieramy tylko id miast trasy rozwiązania
        route = Route(solution_cities, cities)  # tworzymy obiekt Route

        if route.is_valid(self.salesman_max_time):
            # jeżeli rozwiązanie jest poprawne to poinformowanie o tym użytkownika
            self.info_message('Trasa jest poprawna')
        elif route.invalid_cause == 'less than 2 cities':
            # poinformowanie użytkownika, że rozwiązanie jest błędne, bo ma mniej niż 2 miasta
            self.info_message('Trasa składa się z mniej niż dwóch miast')
        elif route.invalid_cause == 'cities not connected':
            # poinformowanie użytkownika, że rozwiązanie jest błędne, bo nie jest możliwe połączenie miast na trasie
            self.info_message('Na trasie sąsiadują ze sobą miasta, które nie są ze sobą połączone')
        elif route.invalid_cause == 'too long':
            # poinformowanie użytkownika, że rozwiązanie jest błędne, bo pokonanie trasy przekracza czas pracy
            # komiwojażera
            self.info_message('Długość trasy przekracza ograniczenie Komiwojażera')
        else:
            # poinformowanie, że trasa nie jest poprawna z innego powodu
            self.info_message('Trasa nie jest poprawna')

    def show_map(self):
        # Metoda przekazuje do kolejki zadań GUI prośbę o pokazanie mapy i informacje o miastach, połączeniach i
        # rozwiązaniu
        action = {'func': self.app.draw_map, 'cities': self.cities, 'connections': self.connections,
                  'route': self.solution}
        self.feedback_queue.put(action)

    def quit(self):
        pass

    @staticmethod
    def _execute_feedback(func, **kwargs):
        # wykonanie funkcji func z argumentami kwargs
        func(**kwargs)


if __name__ == '__main__':
    controller = Controller()
    # controller.read_cities('C:/Users/p/PycharmProjects/Komiwojazer/data/test_cities.csv')
    # controller.read_connections('C:/Users/p/PycharmProjects/Komiwojazer/data/test_roads.csv')
    # controller.read_salesman_max_time('C:/Users/p/PycharmProjects/Komiwojazer/data/test_salesman_timelimit.csv')
    # controller.read_route('C:/Users/p/PycharmProjects/Komiwojazer/data/valid_solution1.csv')
    # controller.show_map()
    # controller.app.animate_graph()
    # controller.find_best_route(time_limit=3)
    # controller.save_solution('C:/Users/p/PycharmProjects/Komiwojazer/data/asd.txt')

    controller.mainloop()




