from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
import random

Builder.load_file('main.kv')


# Clase para las etiquetas de texto ajustadas a su tamaño (wrapped)
class WrappedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = 'center'
        self.bind(
            width=lambda *x:
            self.setter('text_size')(self, (self.width, None)),
            texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))


class VentanaLayout(Screen):
    pass


class MenuPrincipal(Screen):
    pass


class SelectPlayer(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.referencia = App.get_running_app().root.ids.jugarid

    def selection1(self):
        self.referencia.player2 = NPCNash('johnnash.jpg',
                                          ['Buen día, prepárese para reportar las pérdidas más cuantiosas de su vida',
                                           'Llevo esperando este momento desde la salida de mi último libro',
                                           'frase 3'])
        self.dismiss()
        self.referencia.inicio_juego()

    def selection2(self):
        self.referencia.player2 = NPCSmith('adamsmith.jpg',
                                           ['frase 1',
                                            'frase 2',
                                            'frase 3'])
        self.dismiss()
        self.referencia.inicio_juego()

    def selection3(self):
        self.referencia.player2 = NPCMarx('karlmarx.jpg',
                                          ['''Espero trates bien a tus trabajadores, no te quiero ver extrayendo 
                                          plusvalía''',
                                           'frase 999',
                                           'frase 3'])
        self.dismiss()
        self.referencia.inicio_juego()


class ResetGame(Popup):

    def exportar_resultados(self):
        pass


class JugarVentana(VentanaLayout):
    player2 = None
    prod1 = 0
    prod2 = 0
    precio = 0
    beneficio1 = 0
    beneficio2 = 0
    cantidad_total = 0
    evento = 0
    historial = {}
    model = 0
    precio2 = 0

    # Asignamos valores aleatorios al inicio del juego
    a = 0
    b = 0
    c = 0

    # Valores a mostrar en pantalla
    comentario = StringProperty('')
    modelo = StringProperty('')
    narrativa = StringProperty('')
    demanda_mercado = StringProperty(f'{a} - {b}x')
    costes_totales = StringProperty(f'{c}x')
    imagen = StringProperty('')
    rival = None
    stage = NumericProperty(0)
    stage1 = StringProperty('')
    stage2 = StringProperty('')
    stage3 = StringProperty('')

    def on_enter(self, *args):
        if self.stage == 0:
            selector = SelectPlayer()
            selector.open()
        else:
            pass

    def inicio_juego(self):
        # Asignamos valores aleatorios al inicio del juego
        self.a = random.randint(250, 500)
        self.b = random.randint(2, 25)
        self.c = random.randint(21, 40)

        self.imagen = str(self.player2.img)
        self.comentario = self.player2.frases[random.randint(0, 2)]
        self.update_screen()
        self.selecciona_modelo()
        self.stage += 1

    def update_screen(self):
        self.demanda_mercado = f'{self.a} - {self.b}x'
        self.costes_totales = f'{self.c}x'

    def selecciona_modelo(self):
        self.model = random.randint(1, 4)

        # Cournot
        if self.model == 1:
            self.modelo = 'MODELO DE COURNOT'
            self.prod2 = round(self.player2.cournot(self.a, self.b, self.c), 3)

        # NPC Stackelberg líder
        elif self.model == 2:
            self.prod2 = round(self.player2.stackelberg1(self.a, self.b, self.c), 3)
            self.modelo = f'MODELO DE NPC = LÍDER. {self.player2.name} produjo {self.prod2} unidades.'

        # NPC Stackelberg seguidor
        elif self.model == 3:
            self.modelo = 'MODELO DE STACKELBERG NPC = SEGUIDOR'

        # Bertrand
        else:
            self.modelo = 'MODELO DE BERTRAND'
            self.precio2 = self.player2.bertrand(self.c)

    def reset_parametros(self):
        self.historial = {}
        self.stage = 0
        self.ids.respuesta.text = ''
        self.stage1 = ''
        self.stage2 = ''
        self.stage3 = ''
        self.imagen = ''
        self.comentario = ''
        self.modelo = ''
        self.narrativa = ''
        self.demanda_mercado = ''
        self.costes_totales = ''
        NPCSmith.tax = 0

    def evento_aleatorio(self):
        # Selección aleatoria del evento y la cuantía
        self.evento = random.randint(1, 4)
        cuantia = random.randint(3, 10)

        # Si el evento afecta a la demanda, modificamos la demanda (y viceversa)
        if self.evento == 1:
            self.narrativa = '''Recientemente se publicaron los resultados de un estudio llevado a cabo por la\
 universidad de Massachusetts que resaltan los beneficios del uso de tu producto. Esto ha producido un aumento\
 de la demanda de mercado.'''
            self.a = self.a + cuantia

        elif self.evento == 2:
            self.narrativa = '''Como consecuencia de una pandemia mundial, el número de personas que\
 pueden acceder y utilizar tu producto se ha reducido considerablemente. Los cambios se han introducido\
 en la función de demanda del mercado.'''
            self.a = self.a - cuantia

        elif self.evento == 3:
            self.c = self.c + cuantia
            NPCSmith.tax = NPCSmith.tax - cuantia
            self.narrativa = f'''El Gobierno introdujo un impuesto de {cuantia} u.m. sobre la producción.\
 El aumento aumento de costes asociado se ha introducido en tu función de costes.'''

        elif self.evento == 4:
            self.c = self.c - cuantia
            NPCSmith.tax = NPCSmith.tax + cuantia
            self.narrativa = f'''El Gobierno introdujo una subvención de {cuantia} u.m. por cada unidad producida.\
 Los cambios se han introducido en tu función de costes.'''

        self.update_screen()

    def confirma(self):

        # Comprobamos si el usuario introdujo un valor admitido
        try:
            respuesta = round(float(self.ids.respuesta.text), 3)
            if respuesta == 0:
                raise ValueError
        except ValueError:
            print('Introduzca parámetros válidos')
            return

        # Si es modelo de Bertrand, la variable de decisión cambia
        if self.model == 4:
            self.precio2 = self.precio2

            if self.precio2 > respuesta:
                self.precio = respuesta
                self.prod1 = round((self.a - self.precio) / self.b, 3)
                self.prod2 = 0

            elif self.precio2 < respuesta:
                self.precio = self.precio2
                self.prod1 = 0
                self.prod2 = round((self.a - self.precio) / self.b, 3)

            # Por defecto, a igual precio suponemos los clientes se distribuyen equitativamente
            else:
                self.precio = respuesta
                self.prod1 = round((self.a - self.precio) / (2 * self.b), 3)
                self.prod2 = round((self.a - self.precio) / (2 * self.b), 3)

        # Si el NPC es seguidor, debe conocer nuestra producción
        elif self.model == 3:
            self.prod1 = respuesta
            self.prod2 = round(self.player2.stackelberg2(self.a, self.b, self.c, respuesta), 3)
            self.precio = round(self.a - (self.b * (self.prod1 + self.prod2)), 3)

        else:
            self.prod1 = respuesta
            self.precio = round(self.a - (self.b * (self.prod1 + self.prod2)), 3)

        # Si el precio resultante en el mercado es negativo, se establece un precio igual a 0.001
        if self.precio <= 0:
            self.precio = .001

        self.cantidad_total = round(self.prod1 + self.prod2, 3)
        self.beneficio1 = round((self.precio - self.c) * self.prod1, 3)
        self.beneficio2 = round((self.precio - self.c) * self.prod2, 3)

        # Rellenamos el historial
        self.historial[self.stage] = [self.model, self.a, self.b, self.c, self.precio, self.cantidad_total,
                                      self.prod1, self.beneficio1, self.prod2, self.beneficio2]

        stage_dict = {1: 'stage1', 2: 'stage2', 3: 'stage3'}
        stage_key = stage_dict.get(self.stage)
        setattr(self, stage_key, f'Beneficio: {self.beneficio1}')

        # Pasamos de etapa
        self.ids.respuesta.text = ''
        self.stage += 1

        # Comprobamos si el juego se ha acabado
        if self.stage > 3:
            reseteo = ResetGame()
            reseteo.open()
            return

        else:
            self.evento_aleatorio()
            self.selecciona_modelo()

    def obtenermasinfo(self):
        self.manager.current = 'JugarMasInfoScreen'


class NPCNash:
    def __init__(self, img, frases):
        self.img = img
        self.frases = frases
        self.name = 'John Forbes Nash'

    # Cournot
    @staticmethod
    def cournot(a, b, c):
        return (a - c) / (3 * b)

    # Líder
    @staticmethod
    def stackelberg1(a, b, c):
        return (a - c) / (2 * b)

    # Seguidora
    @staticmethod
    def stackelberg2(a, b, c, x1):
        return ((a - c) / (2 * b)) - (x1 / 2)

    # Bertrand
    @staticmethod
    def bertrand(c):
        return c


class NPCSmith:

    # Variable que (des)informará al NPCSmith sobre los impuestos del Gobierno
    tax = 0

    def __init__(self, img, frases):
        self.img = img
        self.frases = frases
        self.name = 'Adam Smith'

    # Cournot
    @staticmethod
    def cournot(a, b, c):
        return (a - (c + NPCSmith.tax)) / (3 * b)

    # Líder
    @staticmethod
    def stackelberg1(a, b, c):
        return (a - (c + NPCSmith.tax)) / (2 * b)

    # Seguidora
    @staticmethod
    def stackelberg2(a, b, c, x1):
        return ((a - (c + NPCSmith.tax)) / (2 * b)) - (x1 / 2)

    # Bertrand
    @staticmethod
    def bertrand(c):
        return c + NPCSmith.tax


class NPCMarx:
    def __init__(self, img, frases):
        self.img = img
        self.frases = frases
        self.name = 'Karl Marx'

    # Cournot
    @staticmethod
    def cournot(a, b, c):
        return (a - (1.2*c)) / (3 * b)

    # Líder
    @staticmethod
    def stackelberg1(a, b, c):
        return (a - (1.2*c)) / (2 * b)

    # Seguidora
    @staticmethod
    def stackelberg2(a, b, c, x1):
        return ((a - (1.2*c)) / (2 * b)) - (x1 / 2)

    # Bertrand
    @staticmethod
    def bertrand(c):
        return 1.2*c


class JugarMasInfoScreen(Screen):
    a = '''El juego consiste en 3 etapas en las que tú, dueño de una empresa, competirás con uno de los tres NPCs'''


class Manager(ScreenManager):
    pass


class kivynomics_for_android(App):
    def build(self):
        return Manager()


if __name__ == '__main__':
    kivynomics_for_android().run()
