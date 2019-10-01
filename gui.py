from queue import Queue
from tkinter import *
from tkinter import filedialog, messagebox

import matplotlib
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

matplotlib.use('TkAgg')
style.use('ggplot')


class TravellingSalesmanApp(Tk):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.is_alive = True
		self.default_settings = None

		# przygotowanie głównego okienka
		container = Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		# przygotowanie poszczególnych stron i podpięcie do głównego okienka
		self.frames = {}  # słownik zawiera strony, które możemy wyświetlić
		for F in (MainPage, GraphPage):
			page_name = F.__name__
			frame = F(parent=container, root=self)
			self.frames[page_name] = frame
			frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame("MainPage")  # pokazuje stronę MainPage
		self.action_queue = Queue()  # kolejka akcji użytkownika, które później będzie odczytywać controller
		self.protocol("WM_DELETE_WINDOW", self.on_quit)  # wykonanie funkcji self.on_quit w momencie zamknięcia

	def show_frame(self, page_name):
		# pokazuje stronę MainPage
		frame = self.frames[page_name]
		frame.tkraise()

	def refresh(self):
		# metoda odświeża okienko aplikacji
		try:
			self.update_idletasks()
			self.update()
		except TclError:
			if self.is_alive:
				raise

	def set_values_to_default(self, n_iterations=None, time_limit=None, population_size=None, elite_size=None,
							  mutation_rate=None):
		# ustawienie domyślnych wartości w polach, które może edytować użytkownik
		if not self.default_settings:
			assert n_iterations is not None \
				   and time_limit is not None \
				   and population_size is not None \
				   and elite_size is not None \
				   and mutation_rate is not None
			self.default_settings = locals()

		self.frames['MainPage'].iterations_text.delete(0, END)  # usunięcie dotychczas wpisanej liczby iteracji
		self.frames['MainPage'].time_limit_text.delete(0, END)  # maksymalnego czasu pracy
		self.frames['MainPage'].population_size_text.delete(0, END)  # rozmiaru populacji
		self.frames['MainPage'].elite_size_text.delete(0, END)  # rozmiaru elity
		self.frames['MainPage'].mutation_rate_text.delete(0, END)  # odsetka mutacji

		self.frames['MainPage'].iterations_text.insert(0, str(
			self.default_settings['n_iterations']))  # wpisanie domyślnej liczby iteracji
		self.frames['MainPage'].time_limit_text.insert(0, str(
			self.default_settings['time_limit']))  # maksymalnego czasu pracy
		self.frames['MainPage'].population_size_text.insert(0, str(
			self.default_settings['population_size']))  # rozmiaru populacji
		self.frames['MainPage'].elite_size_text.insert(0, str(self.default_settings['elite_size']))  # rozmiaru elity
		self.frames['MainPage'].mutation_rate_text.insert(0, str(
			self.default_settings['mutation_rate']))  # odsetka mutacji

	def on_quit(self):
		# podczas zamknięcia okienka wykonywana jest ta funkcja, która w zmiennej self.is_alive
		# zapisuje informację, że to okienko już nie istnieje
		self.is_alive = False

	def load_cities(self):
		# metoda pyta użytkownika o lokalizację pliku z miastami i dodaje akcję użytkownika do kolejki
		# zadań jeśli użytkownik wskaże jakiś plik
		filename = filedialog.askopenfilename()
		action = {'action': 'read_cities', 'filename': filename}
		print(action)
		if filename:
			self.action_queue.put(action)

	def load_connections(self):
		# metoda pyta użytkownika o lokalizację pliku z połączeniami między miastami i dodaje akcję użytkownika do
		# kolejki zadań jeśli użytkownik wskaże jakiś plik
		filename = filedialog.askopenfilename()
		action = {'action': 'read_connections', 'filename': filename}
		print(action)
		if filename:
			self.action_queue.put(action)

	def load_salesman_time_limit(self):
		# metoda pyta użytkownika o lokalizację pliku z czasem pracy komiwojażera i dodaje akcję użytkownika do kolejki
		# zadań jeśli użytkownik wskaże jakiś plik
		filename = filedialog.askopenfilename()
		action = {'action': 'read_salesman_max_time', 'filename': filename}
		print(action)
		if filename:
			self.action_queue.put(action)

	def load_solution(self):
		# metoda pyta użytkownika o lokalizację pliku z rozwiązaniem i dodaje akcję użytkownika do kolejki
		# zadań jeśli użytkownik wskaże jakiś plik
		filename = filedialog.askopenfilename()
		action = {'action': 'load_solution', 'filename': filename}
		print(action)
		if filename:
			self.action_queue.put(action)

	def check_solution(self):
		# metoda dodaje do kolejki zadań akcję sprawdzenia czy rozwiązanie jest poprawne
		action = {'action': 'check_solution'}
		self.action_queue.put(action)
		print(action)

	def export_solution(self):
		# metoda pyta użytkownika o lokalizację gdzie zapisać plik z rozwiązaniem i jeśli lokalizacja zostanie wskazana
		# to dodaje akcję do kolejki zadań
		filename = filedialog.asksaveasfilename()
		action = {'action': 'save_solution', 'filename': filename}
		print(action)
		if filename:
			self.action_queue.put(action)

	def show_map(self):
		# metoda dodaje do kolejki zadań akcję pokazania mapy
		action = {'action': 'show_map'}
		print(action)
		self.action_queue.put(action)

	def draw_map(self, **kwargs):
		# metoda otwiera stronę z mapą i ją rysuje
		self.frames['GraphPage'].tkraise()
		self.frames['GraphPage'].draw_map(**kwargs)

	def find_solution(self):
		# metoda dodaje do kolejki zadań akcję uruchomienia algorytmu z pobranymi z okienka hiperparametrami

		# pobranie danych z okienka
		n_iterations = int(self.frames['MainPage'].iterations_text.get())
		time_limit = float(self.frames['MainPage'].time_limit_text.get())
		population_size = int(self.frames['MainPage'].population_size_text.get())
		elite_size = float(self.frames['MainPage'].elite_size_text.get())
		mutation_rate = float(self.frames['MainPage'].mutation_rate_text.get())
		# utworzenie akcji
		action = {
			'action': 'find_solution',
			'n_iterations': n_iterations,
			'time_limit': time_limit,
			'population_size': population_size,
			'elite_size': elite_size,
			'mutation_rate': mutation_rate
		}
		print(action)
		# dodanie akcji do kolejki zadań
		self.action_queue.put(action)

	def get_user_action(self):
		# metoda zwraca akcję użytkownika oczekującą w kolejce zadań
		# ta metoda będzie wykorzystywana przez controller
		if self.action_queue.empty():
			action = None
		else:
			action = self.action_queue.get_nowait()

		return action

	@staticmethod
	def error_message(message):
		# metoda wyświetla okienko błędu z wiadomością
		messagebox.showerror("Error", message)

	@staticmethod
	def info_message(message):
		# metoda wyświetla okienko informacji z wiadomością
		messagebox.showinfo('Info', message)

	@staticmethod
	def warning_message(message):
		# metoda wyświetla okienko ostrzeżenia z wiadomością
		messagebox.showwarning(message)

	def block_buttons(self):
		# metoda blokuje działanie przycisków
		print('blocking')
		print(self.frames['MainPage'].buttons)
		for button in self.frames['MainPage'].buttons:
			button.configure(state=DISABLED)

	def unblock_buttons(self):
		# metoda odblokowuje działanie przycisków
		for button in self.frames['MainPage'].buttons:
			button.configure(state=NORMAL)


class MainPage(Frame):
	# klasa zawiera wygląd głównej strony aplikacji
	def __init__(self, parent, root):
		# stworzenie strony
		super().__init__(parent)
		self.root = root

		# ustawienie siatki
		self.grid(row=0, column=0, sticky=NSEW)

		# wczytywanie mapy i danych komiwojażera
		# przycisk wczytywania miast
		load_cities_button = Button(self, text='Wczytaj listę miast', command=self.root.load_cities)
		load_cities_button.grid(column=0, sticky=EW)

		# przycisk wczytywania połączeń
		load_connections_button = Button(self, text='Wczytaj listę połączeń między miastami',
										 command=self.root.load_connections)
		load_connections_button.grid(column=0, sticky=EW)

		# przycisk wczytywania czasu pracy komiwojażera
		load_salesman_time_limit = Button(self, text='Wczytaj czas pracy Komiwojażera',
										  command=self.root.load_salesman_time_limit)
		load_salesman_time_limit.grid(column=0, sticky=EW)

		# Praca nad rozwiązaniem
		# przycisk wczytywania rozwiązania
		load_solution_button = Button(self, text='Wczytaj rozwiazanie', command=self.root.load_solution)
		load_solution_button.grid(pady=(10, 0), column=0, sticky=EW)

		# przycisk sprawdzenia poprawności rozwiązania
		check_solution_button = Button(self, text='Zweryfikuj rozwiązanie', command=self.root.check_solution)
		check_solution_button.grid(column=0, sticky=EW)

		# przycisk zapisywania rozwiązania
		export_solution_button = Button(self, text='Eksportuj rozwiązanie', command=self.root.export_solution)
		export_solution_button.grid(column=0, sticky=EW)

		# wizualizacja mapy
		# przycisk do pokazania mapy
		show_map_button = Button(self, text='Pokaż mapę', command=self.root.show_map)
		show_map_button.grid(pady=(10, 0), column=0, sticky=EW)

		# quit_button = Button(self, text='Quit', command=self.client_exit)
		# quit_button.grid(pady=(10, 0), column=0, sticky=EW)

		# belka z napisem ustawienia
		self.settings_label = Label(self, text='Ustawienia algorytmu', width=50)
		self.settings_label.grid(row=0, column=1, columnspan=2, sticky=EW)

		# pole do wpisania maks. liczby iteracji
		self.iterations_label = Label(self, text='Maksymalna liczba iteracji')
		self.iterations_label.grid(row=1, column=1, sticky=EW)
		self.iterations_text = Entry(self, width=10)
		self.iterations_text.grid(row=1, column=2, sticky=EW)

		# pole do wpisania maksymalnego czasu optymalizacji
		self.time_limit_label = Label(self, text='Maksymalny czas optymalizacji')
		self.time_limit_label.grid(row=2, column=1, sticky=EW)
		self.time_limit_text = Entry(self, width=10)
		self.time_limit_text.grid(row=2, column=2, sticky=EW)

		# pole do wpisania wielkości populacji
		self.population_size_label = Label(self, text='Wielkość populacji')
		self.population_size_label.grid(row=3, column=1, sticky=EW)
		self.population_size_text = Entry(self, width=10)
		self.population_size_text.grid(row=3, column=2, sticky=EW)

		# pole do wpisania odsetku elity
		self.elite_size_label = Label(self, text='Odsetek elity')
		self.elite_size_label.grid(row=4, column=1, sticky=EW)
		self.elite_size_text = Entry(self, width=10)
		self.elite_size_text.grid(row=4, column=2, sticky=EW)

		# pole do wpisania odsetka mutacji
		self.mutation_rate_label = Label(self, text='Odsetek mutacji')
		self.mutation_rate_label.grid(row=5, column=1, sticky=EW)
		self.mutation_rate_text = Entry(self, width=10)
		self.mutation_rate_text.grid(row=5, column=2, sticky=EW)

		# przycisk do uruchomienia algorytmu szukającego optymalnej trasy
		find_solution_button = Button(self, text='Znajdź najlepsze rozwiązanie', command=self.root.find_solution)
		find_solution_button.grid(row=6, column=1, columnspan=2, pady=(10, 0), sticky=EW)

		# lista zawierająca wszystkie przyciski
		self.buttons = [load_cities_button, load_connections_button, load_salesman_time_limit, load_solution_button,
						check_solution_button, export_solution_button, show_map_button, find_solution_button]


class GraphPage(Frame):
	# klasa zawiera stronę pokazującą mapę miast, połączeń i drogi
	def __init__(self, parent, root):
		# stworzenie strony
		super().__init__(parent)
		self.root = root
		self.fig = None  # tu będzie pole wykresu
		self.ax = None  # tu będą wykresy
		self.canvas = None  # tu będzie pole na stronie, na którym znajdą się fig, ax i toolbar
		self.toolbar = None  # tu będzie pasek poruszania się po wykresie
		self.widget = None

		# przycisk powrotu do strony głównej
		button1 = Button(self, text="Powrót", command=lambda: root.show_frame("MainPage"))
		button1.pack()

	def draw_map(self, cities, connections, route):
		# usunięcie wykresu jeśli jakiś istniał
		if self.toolbar:
			self.toolbar.destroy()
		if self.widget:
			self.widget.destroy()

		# przygotowanie elementów wykresu
		self.fig = Figure(figsize=(5, 5), dpi=100)
		self.ax = self.fig.add_subplot(111)

		# przygotowanie miejsca na wykresy
		self.canvas = FigureCanvasTkAgg(self.fig, self)
		self.canvas.draw()
		self.widget = self.canvas.get_tk_widget()
		self.widget.pack(side=TOP, fill=BOTH, expand=True)

		# stworzenie paska nawigacji
		self.toolbar = NavigationToolbar2Tk(self.canvas, self)
		self.toolbar.update()
		self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

		# wyczyszczenie wykresu, jeśli jakiś istniał
		self.ax.clear()

		# naniesienie miast na mapę jeśli zostały wczytane
		if cities:
			xs = [city[1] for city in cities]
			ys = [city[2] for city in cities]
			self.ax.scatter(xs, ys, s=100, color='b')

		# naniesienie połączeń między miastami, jeśli zistały wczytane zarówno miasta jak i połączenia
		if cities and connections:
			city2coords = dict()
			for city_name, x, y, profit in cities:
				city2coords[city_name] = (x, y)

			for city1, city2, distance in connections:
				road = self.get_road_from_city_to_city(city2coords[city1], city2coords[city2])
				xs = [coords[0] for coords in road]
				ys = [coords[1] for coords in road]
				self.ax.plot(xs, ys, color='b', linewidth=5)

		# naniesienie na mapę trasy, jeśli została wczytana
		if route:
			previous_city = route[0][1:3]
			for city_name, x, y, distance in route[1:]:
				next_city = [x, y]
				road = self.get_road_from_city_to_city(previous_city, next_city)

				xs = [row[0] for row in road]
				ys = [row[1] for row in road]
				self.ax.plot(xs, ys, color='r', linewidth=3)
				previous_city = next_city

		self.fig.canvas.draw_idle()

	@staticmethod
	def get_road_from_city_to_city(city1, city2):
		# metoda zwraca współrzędne drogi, która łączy dane miasta w układzie manhattan. Metoda zakłada, że miasta są
		# ze sobą bezpośrednio połączone
		c1x, c1y = city1
		c2x, c2y = city2
		if c1x >= c2x:
			if c1y >= c2y:
				road = [city1, [c1x, c2y], city2]
			else:
				road = [city1, [c1x, c2y], city2]
		else:
			if c1y >= c2y:
				road = [city1, [c2x, c1y], city2]
			else:
				road = [city1, [c2x, c1y], city2]
		return road


if __name__ == '__main__':
	app = TravellingSalesmanApp()
	app.mainloop()
# while True:
#     app.refresh()
