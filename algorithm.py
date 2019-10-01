import copy
import random
import time

"""
file:///home/p/Downloads/import_contents_BPB1-0047-0012-httpwww_wi_pb_edu_plplikinaukazeszytyz5piwonska-full.pdf
"""


class City:
    # Klasa opisująca miasto
    def __init__(self, id_, x, y, profit):
        self.id = id_
        self.x = x
        self.y = y
        self.profit = profit
        self.connected_cities = dict()  # dict(city_id: distance)

    def distance(self, city):
        # oblicza odległość z jednego miasta do drugiego
        if isinstance(city, City):
            city = city.id
        return self.connected_cities[city]

    def add_connection(self, city_id, distance):
        # dodaje inne miasto, do którego połączone jest obecne i odległość między nimi
        self.connected_cities[city_id] = distance

    def __repr__(self):
        # opisuje jak wyświetlić miasto jeśli będziemy chcieli je wyprintować
        return f'City({self.id}, {self.x}, {self.y})'

    def __eq__(self, other):
        # opisuje jak porównywać dwa miasta, aby sprawdzić czy to jest to samo miasto
        if not isinstance(other, type(self)):
            return False
        return self.x == other.x and self.y == other.y


class Route:
    # klasa opisuje metody dotyczące trasy
    def __init__(self, route, cities):
        assert isinstance(route, list) or isinstance(route, tuple)
        self.route = route  # list or tuple of city ids
        self.cities = cities  # dict(id: City)
        self._distance = None  # długość trasy
        self._fitness = None  # zysk komiwojażera na trasie
        self.valid = None  # czy to jest poprawna trasa
        self.invalid_cause = None  # przyczyna z jakiej trasa jest niepoprawna

    @property
    def distance(self):
        # metoda oblicza i podaje odległość trasy
        if self._distance is None:
            distance = 0
            if self.route:
                previous_city_id = self.route[0]
                for current_city_id in self.route[1:]:
                    distance += self.cities[previous_city_id].distance(current_city_id)
                    previous_city_id = current_city_id

            self._distance = distance

        return self._distance

    @property
    def fitness(self):
        # metoda oblicza i podaje zysk na trasie
        if self._fitness is None:
            visited_cities = set()
            fitness = 0
            if self.route:
                for current_city_id in self.route:
                    if current_city_id not in visited_cities:
                        visited_cities.add(current_city_id)
                        fitness += self.cities[current_city_id].profit
            self._fitness = fitness

        return self._fitness

    def correct_connections(self):
        # metoda sprawdza czy połączenia trasy są poprawne
        for idx in range(len(self.route) - 1):
            current_city = self.route[idx]
            next_city_id = self.route[idx + 1]
            if next_city_id not in self.cities[current_city].connected_cities:
                return False
        else:
            return True

    def is_valid(self, max_distance):
        # metoda sprawdza czy trasa jest poprawna
        if self.valid is None:

            if len(self.route) < 2:
                self.valid = False
                self.invalid_cause = 'less than 2 cities'
                return self.valid

            elif not self.correct_connections():
                self.valid = False
                self.invalid_cause = 'cities not connected'
                return self.valid

            elif self.distance > max_distance:
                self.valid = False
                self.invalid_cause = 'too long'
                return self.valid

            else:
                self.valid = True

        return self.valid

    def get_route_coordinates(self):
        # metoda zwraca współrzędne miast na trasie
        coordinates = []
        for city_id in self.route:
            city = self.cities[city_id]
            x = city.x
            y = city.y
            coordinates.append([x, y])
        return coordinates


class GeneticAlgorithm:
    # algorytm optymalizujący trasę komiwojażera
    DEFAULT_SETTINGS = {'n_iterations': 1000, 'population_size': 1000, 'mutation_rate': 0.05, 'elite_size': 0.5,
                        'time_limit': 15}

    def __init__(self, cities, roads, max_distance):
        self.cities = self.construct_cities(cities, roads)  # wczytane miasta
        self.max_distance = max_distance  # maksymalny dystans / czas pracy Komiwojażera

    def find_optimal_route(self, n_iterations=None, population_size=None, mutation_rate=None, elite_size=None,
                           time_limit=None, verbose=True):
        # wybranie domyślnych wartości hiperparametrów, jeśli nie zostały podane
        if n_iterations is None:
            n_iterations = self.DEFAULT_SETTINGS['n_iterations']

        if population_size is None:
            population_size = self.DEFAULT_SETTINGS['population_size']

        if mutation_rate is None:
            mutation_rate = self.DEFAULT_SETTINGS['mutation_rate']

        if elite_size is None:
            elite_size = self.DEFAULT_SETTINGS['elite_size']
        elite_size = int(population_size * elite_size)

        if time_limit is None:
            time_limit = self.DEFAULT_SETTINGS['time_limit']

        start = time.time()
        best_fit_per_iteration = []  # historia optymalizacji
        population = self._create_first_population(population_size)

        # główna pętli optymalizacji
        for iteration in range(n_iterations):
            ranked_population = self.rank_routes(population)  # oceniamy populację
            best_route = ranked_population[0]
            elite = self._select_best_individuals(ranked_population, elite_size)  # i wybieramy najlepsze trasy

            # wydrukowanie niektórych danych w czasie optymalizacji
            if verbose:
                fitnesses = [individual.fitness for individual in ranked_population]
                avg_score = sum(fitnesses) / len(fitnesses)
                print(iteration, best_route.fitness, avg_score)

            # zapisanie najlepszego wyników w iteracji
            best_fit_per_iteration.append((iteration, best_route.fitness, best_route))

            # przerwanie pracy jeśli optymalizacja przekroczyła dozwolony czas
            if time.time() - start > time_limit:
                print(f'Optimization terminated due to time limit after {iteration} iterations')
                break

            children = self._breed_population(elite, population_size)  # tworzenie dzieci
            population = self._mutate_population(children, mutation_rate)  # mutacje

        # wybranie najlepszego wyników w historii iteracji i zwrócenie jako wynik
        *other, best_score, best_route = sorted(best_fit_per_iteration, key=lambda r: r[1], reverse=True)[0]
        return best_route

    @staticmethod
    def construct_cities(cities, roads):
        # przekształcenie surowych danych na obiekty typu City
        constructed_cities = dict()
        for city_id, x, y, profit in cities:
            constructed_cities[city_id] = City(city_id, x, y, profit)

        for city1, city2, distance in roads:
            constructed_cities[city1].add_connection(city2, distance)
            constructed_cities[city2].add_connection(city1, distance)

        return constructed_cities

    def _create_initial_route(self):
        # przygotowanie losowej, ale poprawnej trasy
        starting_city = random.choice(list(self.cities.values()))  # wybranie losowego miasta początkowego
        route_cities = [starting_city]
        route_ids = [starting_city.id]
        distance = 0
        while True:
            # wybranie losowego, jeszcze nieodwiedzonego miasta, które można dołączyć do trasy
            possible_next_cities = route_cities[-1].connected_cities
            unvisited_possible_next_cities = [[c_id, d] for c_id, d in possible_next_cities.items()
                                              if c_id not in route_ids]
            if unvisited_possible_next_cities:
                next_city, distance_to_city = random.choice(unvisited_possible_next_cities)
            else:
                # jeśli nie ma nieodwiedzonych miast to wybieramy losowo odwiedzone
                next_city, distance_to_city = random.choice(list(possible_next_cities.items()))

            # dodajemy miasto do trasy jeśli łączna długość nie przekroczy limitu czasu pracy Komiwojażera
            # w przeciwnym wypadku nie dodajemy i zwracamy trasę
            if distance + distance_to_city > self.max_distance:
                return route_ids
            else:
                route_cities.append(self.cities[next_city])
                route_ids.append(next_city)
                distance += distance_to_city

    def _create_first_population(self, population_size):
        # przygotowanie początkowej losowej populacji
        init_population = []
        while len(init_population) < population_size:
            individual = self._create_initial_route()
            individual = Route(individual, self.cities)
            if individual.is_valid(self.max_distance):
                init_population.append(individual)
        return init_population

    @staticmethod
    def rank_routes(population):
        # posortowanie tras względem zysku, który przynoszą
        return list(sorted(population, key=lambda individual: individual.fitness, reverse=True))

    @staticmethod
    def _select_best_individuals(ranked_population, elite_size):
        # wybranie najlepszych tras
        # TODO można dodać trochę losowości
        return ranked_population[:elite_size]

    def _breed_population(self, mating_pool, population_size):
        # rozmnożenie populacji do czasu uzyskania wymaganej liczebności
        children = list(copy.copy(mating_pool))

        while len(children) < population_size:
            p1, p2 = random.choices(mating_pool, k=2)
            offspring = self._breed(p1, p2)
            if not offspring:
                continue
            else:
                children += offspring
        return children

    def _breed(self, p1, p2):
        # skrzyżowanie dwóch tras w celu uzyskania dzieci
        children = []
        # jeśli rodzice nie mają wspólnych miast to nie są w stanie stworzyć potomstwa
        common_genes = set(p1.route) & set(p2.route)
        if not common_genes:
            return children

        # wybranie wspólnego genu, w miejscu którego nastąpi krzyżowanie
        gene_for_division = random.choice(list(common_genes))
        p1_indices_of_division_gene = [idx for idx, x in enumerate(p1.route) if x == gene_for_division]
        p2_indices_of_division_gene = [idx for idx, x in enumerate(p2.route) if x == gene_for_division]

        p1_gene_idx = random.choice(p1_indices_of_division_gene)
        p2_gene_idx = random.choice(p2_indices_of_division_gene)

        # krzyżowanie
        c1 = p1.route[:p1_gene_idx] + p2.route[p2_gene_idx:]
        c2 = p1.route[:p2_gene_idx] + p2.route[p1_gene_idx:]

        # stworzenie dzieci
        c1 = Route(c1, self.cities)
        c2 = Route(c2, self.cities)

        # zwrócenie tylko tych tras, które są poprawne
        if c1.is_valid(self.max_distance):
            children.append(c1)

        if c2.is_valid(self.max_distance):
            children.append(c2)

        return children

    def _mutate(self, individual, mutation_rate):
        # dokonanie mutacji w losowym miejscu jeśli jest to możliwe

        if random.random() > mutation_rate:
            return individual
        route = copy.copy(individual.route)
        # route = individual.route
        # wybieramy punkt, w którym dokonamy mutacji i dodajemy losowe miasto, które jest wspólne dla obu miast wokół
        # tego punktu
        insertion_point = random.choice(('start', 'end'))
        if insertion_point == 'start':
            city = route[0]
            random_neighbour = random.choice(list(self.cities[city].connected_cities.keys()))
            new_route = [random_neighbour] + route
        else:
            city = route[-1]
            random_neighbour = random.choice(list(self.cities[city].connected_cities.keys()))
            new_route = route + [random_neighbour]
        # else:
        #     city1 = route[insertion_point - 1]
        #     city2 = route[insertion_point]
        #     common_neighbours = set(self.cities[city1].connected_cities.keys()) \
        #                         | set(self.cities[city2].connected_cities.keys())
        #
        #     if not common_neighbours:
        #         return individual
        #
        #     common_neighbour = random.choice(list(common_neighbours))
        #     new_route = route[:insertion_point] = [common_neighbour] + route[insertion_point:]

        # stworzenie nowej trasy i zwrócenie jej tylko w przypadku gdy jest poprawna
        mutant = Route(new_route, self.cities)

        if mutant.is_valid(self.max_distance):
            return mutant
        else:
            return individual

    def _mutate_population(self, population, mutation_rate):
        # przeprowadzenie mutacji na całej populacji
        return tuple(self._mutate(individual, mutation_rate) for individual in population)
