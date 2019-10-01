import unittest

from algorithm import City, Route, GeneticAlgorithm
import IO


class TestCaseCity(unittest.TestCase):
	def setUp(self):
		self.test_city = City('miasto_testowe', 1, 1, 5)
		self.test_city.add_connection('Miasto2', 5)
		self.test_city.add_connection('Miasto3', 6)

	def distance1(self):
		assert self.test_city.distance('Miasto2') == 5, 'Źle oblicza odległość do miasta'

	def distance2(self):
		assert self.test_city.distance('Miasto3') == 6, 'Źle oblicza odległość do miasta'

	def distance3(self):
		try:
			self.test_city.distance('')
			raise AssertionError('Miasto nie istnieje więc nie powinna zostać podana odległość')
		except KeyError:
			pass

	def distance4(self):
		try:
			self.test_city.distance('')
			raise AssertionError('Miasto nie istnieje więc nie powinna zostać podana odległość')
		except KeyError:
			pass

	def distance5(self):
		try:
			self.test_city.distance(5)
			raise AssertionError('Miasto nie istnieje więc nie powinna zostać podana odległość')
		except KeyError:
			pass

	def distance6(self):
		try:
			self.test_city.distance(None)
			raise AssertionError('Miasto nie istnieje więc nie powinna zostać podana odległość')
		except KeyError:
			pass

	def distance7(self):
		try:
			self.test_city.distance('Nieistniejące miasto')
			raise AssertionError('Miasto nie istnieje więc nie powinna zostać podana odległość')
		except KeyError:
			pass

	def comparison1(self):
		assert self.test_city != 5, 'Źle porównuje miasta'

	def comparison2(self):
		assert self.test_city != 'miasto_testowe', 'Źle porównuje miasta'

	def comparison3(self):
		assert self.test_city != (1, 1), 'Źle porównuje miasta'

	def comparison4(self):
		assert self.test_city == City('miasto_testowe', 1, 1, 5), 'Źle porównuje miasta'

	def comparison5(self):
		assert self.test_city == City('inne_miasto_o_tych_samych_współrzędnych', 1, 1, 7), 'Źle porównuje miasta'


class TestRoute(unittest.TestCase):
	def setUp(self):
		self.cities = {'Miasto1': City('Miasto1', 1, 1, 5), 'Miasto2': City('Miasto2', 2, 2, 4),
					   'Miasto3': City('Miasto3', 2, 2, 6)}
		self.connections = [('Miasto1', 'Miasto2', 2)]
		self.cities['Miasto1'].add_connection('Miasto2', 2)
		self.cities['Miasto2'].add_connection('Miasto1', 2)

	def test_valid1(self):
		test_route = Route(['Miasto1', 'Miasto2'], self.cities)
		assert test_route.is_valid(5) is True, 'Źle sprawdza poprawność trasy'

	def test_valid2(self):
		test_route = Route(['Miasto1', 'Miasto2'], self.cities)
		assert test_route.is_valid(1) is False, 'Źle sprawdza poprawność trasy'
		assert test_route.invalid_cause == 'too long', 'Zła przyczyna niepoprawności trasy'

	def test_valid3(self):
		test_route = Route(['Miasto1', 'Miasto3'], self.cities)
		assert test_route.is_valid(5) is False, 'Źle sprawdza poprawność trasy'
		assert test_route.invalid_cause == 'cities not connected', 'Zła przyczyna niepoprawności trasy'

	def test_valid4(self):
		test_route = Route(['Miasto1'], self.cities)
		assert test_route.is_valid(5) is False, 'Źle sprawdza poprawność trasy'
		assert test_route.invalid_cause == 'less than 2 cities', 'Zła przyczyna niepoprawności trasy'

	def test_valid5(self):
		test_route = Route([], self.cities)
		assert test_route.is_valid(5) is False, 'Źle sprawdza poprawność trasy'
		assert test_route.invalid_cause == 'too long', 'Zła przyczyna niepoprawności trasy'

	def test_distance1(self):
		test_route = Route(['Miasto1', 'Miasto2'], self.cities)
		assert test_route.distance == 2, 'Źle oblicza odległość trasy'

	def test_distance2(self):
		test_route = Route(['Miasto1'], self.cities)
		assert test_route.distance == 0, 'Źle oblicza odległość trasy'

	def test_distance3(self):
		test_route = Route([], self.cities)
		assert test_route.distance == 0, 'Źle oblicza odległość trasy'

	def test_fitness1(self):
		test_route = Route(['Miasto1', 'Miasto2'], self.cities)
		assert test_route.fitness == 9, 'Źle oblicza zysk na trasie'

	def test_fitness2(self):
		test_route = Route(['Miasto1'], self.cities)
		assert test_route.fitness == 5, 'Źle oblicza zysk na trasie'

	def test_fitness3(self):
		test_route = Route([], self.cities)
		assert test_route.fitness == 0, 'Źle oblicza zysk na trasie'


class TestCaseIO(unittest.TestCase):
	def setUp(self):
		pass

	def test_load_route(self):
		solution = IO.read_solution('test_data1/valid_solution1.csv')
		assert solution == ([['Miasto1', 1.0, 3.0, 4.0], ['Miasto2', 2.0, 2.0, 5.0], ['Miasto3', 3.0, 1.0, 6.0]], 15.0, 3.0), 'Niepoprawnie wczytane dane rozwiązania'


class TestCaseGA(unittest.TestCase):
	def setUp(self):
		self.cities = [('Miasto1', 1, 1, 5), ('Miasto2', 2, 2, 4), ('Miasto3', 2, 2, 6)]
		self.connections = [('Miasto1', 'Miasto2', 2)]

	def test_construct_cities(self):
		cities = GeneticAlgorithm.construct_cities(self.cities, self.connections)
		assert cities == {'Miasto1': City('Miasto1', 1, 1, 5), 'Miasto2': City('Miasto2', 2, 2, 4),
						  'Miasto3': City('Miasto3', 2, 2, 6)}

		assert cities['Miasto1'].connected_cities == {'Miasto2': 2}
		assert cities['Miasto2'].connected_cities == {'Miasto1': 2}
		assert cities['Miasto3'].connected_cities == dict()


if __name__ == '__main__':
	unittest.main()
