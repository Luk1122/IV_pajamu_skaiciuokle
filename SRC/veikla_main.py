import random
from datetime import datetime
import sqlite3
import json
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
import seaborn as sns
#vietoj ??? įrašyti sukompiliuoto UI failo kelią
from GUI.Ui_veikla_gui import Ui_MainWindow
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg') # matplpotlib liepiam naudoti pyqt5 framework'a
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# 12-13 el: importuojame bibliotekas kurios mokes pyqt lange atvaizduti grafika

# GPM, VSD, PSD mokesciai


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.langas = Ui_MainWindow()
        self.langas.setupUi(self)
        # aprašomos mygtukų funkcijos
        self.langas.actionClose.triggered.connect(self.close_function)
        self.langas.write_data_button.clicked.connect(self.write_button_function)
        self.langas.trinti_button.clicked.connect(self.trinti_button_function)
        self.langas.duomenys_button.clicked.connect(self.simplot)
        self.langas.skaiciuoti_button.clicked.connect(self.skaiciuoti_button_function)
        # iškviečiam reikiamus modulius
        # susikuriam vartotojo įvesties lentelę
        self.set_data_table()
        self.load_data_db()
        # apsirasom matplotlibo grafika
        self.fig, self.ax = plt.subplots()
        self.plotcanvas = FigureCanvas(self.fig) # remelis su grafiku
        grid = QtWidgets.QGridLayout() # veikia resize
        navigacija = NavigationToolbar(self.plotcanvas)
        grid.addWidget(navigacija)
        grid.addWidget(self.plotcanvas)
        self.langas.grafikas.setLayout(grid)
        self.plotcanvas.draw()
        pass
        
    
    def simplot(self):
        y = np.random.randint(1, 11, 10)
        x = np.arange(1, 11)
        
        self.ax.clear() # isvalome ankstesnius grafikus, jei tokiu buvo
        # self.ax.plot(x, y, label="svabus grafikas")
        sns.lineplot(x=x, y=y, label='seaborn', ax=self.ax)
        self.ax.legend(loc='best')
        self.plotcanvas.draw()
        pass
    
    
    def close_function(self):
        sys.exit(0)
        
    
    # Funkcija patikrina ar datos formatas tinkamas
    def is_valid_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
        
    # # # Funkcija patikrinti ar nesumaišyti datos stulpeliai
    # def validate_dates(self, date_from, date_to, date_format="%Y-%m-%d"):
    #     # paverčiame į datetime objektus
    #     # date_from = str(date_from)
    #     # date_to = str(date_to)
    #     date_from_obj = datetime.strptime(date_from, date_format)
    #     date_to_obj = datetime.strptime(date_to, date_format)

    #     if date_from_obj <= date_to_obj:
    #         return True
    #     else:
    #         return False
    
    
    def write_button_function(self):
        # sukuriam/prisijungniam prie DB
        db = sqlite3.connect('veikla.db')
        C = db.cursor()
        sql = '''create table if not exists saskaitos
        (
            Nr text not null unique,
            data, text
            pirkejas text,
            paslauga text,
            suma float
        )
        '''
        C.execute(sql)
        
        # Sukuriam duomenys dict
        duomenys = {
            'Nr': np.nan, 
            'data': np.nan,
            'pirkėjas': np.nan, 
            'paslauga': np.nan,
            'suma': np.nan
        }
        # Atnaujinam duomenys dict pagal naudotojo įvestis
        for column, col_name in enumerate(duomenys.keys()):
            item = self.langas.tableWidget.item(0, column)
            text = item.text()
            duomenys[col_name] = text
        
        # Patikrina ar Nr nėra tuščias
        if duomenys['Nr'] == '':
            t = 'Neįrašyta. Sąsaitos Nr negali būti tuščias.'
            self.langas.write_data_label.setText(t)
            return
        
        # Patikrina ar data nėra tuščia
        if duomenys['data'] == '':
            t = 'Neįrašyta. Prašome įrašyti sąsaitos datą.'
            self.langas.write_data_label.setText(t)
            return
        
        # Patikrina ar sume nėra tuščia
        if duomenys['suma'] == '':
            t = 'Neįrašyta. Prašome įrašyti sąskaitos sumą.'
            self.langas.write_data_label.setText(t)
            return
        
        # patikrina ar datos formatas tinkamas
        if self.is_valid_date(duomenys['data']) is False:
            t = 'Neįrašyta. Datą reikia įvesti formatu "yyyy-mm-dd"'
            self.langas.write_data_label.setText(t)
            return
        
        # # patikrina ar datos įvestos reikiamu formatu
        # if self.is_valid_date(duomenys['nuo_kada']) is False:
        #     t = 'Neįrašyta. Stulpelyje "nuo_kada" datą reikia įvesti formatu "yyyy-mm-dd"'
        #     self.langas.write_data_label.setText(t)
        #     return
        
        # if self.is_valid_date(duomenys['iki_kada']) is False:
        #     t = 'Neįrašyta. Stulpelyje "iki_kada" datą reikia įvesti formatu "yyyy-mm-dd"'
        #     self.langas.write_data_label.setText(t)
        #     return
        
        # if  self.validate_dates(duomenys['nuo_kada'], duomenys['iki_kada']) is False:
        #     t = 'Neįrašyta. Patikrinkite ar data "nuo_kada" nesumaišyta su data "iki_kada".'
        #     self.langas.write_data_label.setText(t)
        #     return
        


        
        try:
            # įrašom į lentelę
            data = duomenys.values()
            sql = '''insert into saskaitos  values ({n})'''
            q = ['?' for i in range(0, len(data))]
            q_ = ', '.join(q)
            r_ = sql.format(n=q_)
            # print(r_)
            C.executemany(r_, [tuple(data)])
            # C.executemany(r_, tuple(data))

            # sql = '''insert into saskaitos
            # values (?,?,?,?,?,?,?)'''
            # C.executemany(sql, [tuple(data)])
            db.commit()
            db.close()
            
            # write_data_label
            t = 'Įrašyti duomenys -> '+ str(data)
            self.langas.write_data_label.setText(t)
            # išvalom lentelę ir vėl sukuriam lentelę
            db.close()
            self.langas.tableWidget.clear()
            self.set_data_table()
            self.load_data_db()
            
        except sqlite3.IntegrityError as e:
            t = 'Neįrašyta. Sąskaitos Nr turi būti unikalus.'
            self.langas.write_data_label.setText(t)
            
        except Exception as e:
            t = f'Ivyko klaida: {e}'
            self.langas.write_data_label.setText(t)

        finally:
        #     # išvalom lentelę ir vėl sukuriam lentelę
            db.close()
        #     self.langas.tableWidget.clear()
        #     self.set_data_table()
        #     self.load_data_db()
        
                

        
        
    def set_data_table(self):
        stulpeliai = ['Nr', 'Data', 'Pirkėjas', 'Paslauga', 'Suma']
        self.langas.tableWidget.clear()
        self.langas.tableWidget.setRowCount(1)
        self.langas.tableWidget.setColumnCount(len(stulpeliai))
        # su setHorizontalHeaderLabels() sugalvoti reikiamus stulpelius
        self.langas.tableWidget.setHorizontalHeaderLabels(stulpeliai)
        for column_index in range(self.langas.tableWidget.columnCount()):
            item = QtWidgets.QTableWidgetItem()
            self.langas.tableWidget.setItem(0, column_index, item)
        pass
    
    
    def load_data_db(self):
        db = sqlite3.connect('veikla.db')
        C = db.cursor()
        
        # patikrinam ar lentelė 'saskaitos' egzistuoja
        C.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saskaitos'")
        table_exists = C.fetchone()

        if not table_exists:
            db.close()
            return  # or use pass
        
        sql = '''select * from saskaitos
        '''
        s = C.execute(sql)
        ans = C.fetchall()
        
        names = list(zip(*s.description))[0]
        
        ans = list(map(list, zip(*ans)))
        self.langas.lentele2.clear()
        if len(ans) > 0: 
            self.langas.lentele2.setRowCount(len(ans[0]))
            self.langas.lentele2.setColumnCount(len(ans))
        
        stulpeliai = ['Nr', 'Data', 'Pirkėjas', 'Paslauga', 'Suma']
        # self.langas.lentele2.setHorizontalHeaderLabels(names)
        self.langas.lentele2.setHorizontalHeaderLabels(stulpeliai)
        
        for col in range(len(ans)):
            c = ans[col] # pasiimama is stulpeliu saraso konkretu stulpeli
            for row in range(len(c)):
                item = QtWidgets.QTableWidgetItem()
                item.setData(QtCore.Qt.DisplayRole, c[row])
                self.langas.lentele2.setItem(row, col, item)
        
        db.close()
        
    
        pass
    
    # delete from saskaitos where Nr = <Numeris iš pasirinktos eilutės>
    # delete from saskaitos where Nr = "text"
    # delete from saskaitos where Nr = 5 # siuo atveju trins saskaitas kurios nr 5
    def trinti_button_function(self):
        row = self.langas.lentele2.currentRow()
        item = self.langas.lentele2.item(row, 0)
        if item is None:
            return
        item_text = item.text()
        
        db = sqlite3.connect('veikla.db')
        C = db.cursor()
        sql = "DELETE FROM saskaitos WHERE Nr = ?"
        C.execute(sql, (item_text,))  # Use tuple with a comma for a single value
        db.commit()
        db.close()
        
        # self.set_data_table()
        self.load_data_db()
        pass
    
    
    def skaiciuoti_button_function(self):
        metai = self.langas.metaiLine.text()
        # prisijungiam prie db ir norimiems metams suskaičiuojama pajamų sumą
        db = sqlite3.connect('veikla.db')
        C = db.cursor()
        sql = '''
        SELECT SUM(suma)
        FROM saskaitos
        WHERE strftime('%Y', data) = ?
        '''
        C.execute(sql, (str(metai),))  # Use a parameterized query with the year
        ans = C.fetchall()

        sql = '''
        SELECT DISTINCT SUBSTR(data, 1, 4) AS year
        FROM saskaitos
        ORDER BY year;
        '''
        C.execute(sql)
        ans2 = C.fetchall()

        db.close()
        suma_list = list(map(list, zip(*ans)))
        suma = suma_list[0][0] # turim float

        metai_list = list(map(list, zip(*ans2)))

        if metai in metai_list[0]:
            pajamos =f'{suma}'
            self.langas.pajamos_label.setText(pajamos)

            apmokestinamos_pajamos = round(float(pajamos) * 0.7, 2) # 30 proc. išlaidos
            self.langas.apmokestinamos_pajamos_label.setText(str(apmokestinamos_pajamos))

            # skaičiuojam valstybinį socialinį draudimą
            # vdu_2025 = 2108.88
            # vdu_2024 = 1902.7
            # vdu_2023 = 1684.9
            # if metai =='2025':
            #     vdu = 2108.88
            # elif metai =='2024':
            #     vdu = 1902.7
            # elif metai == '2023':
            #     vdu = 1684.9
            

            # lubos = vdu * 43
            lubos = 5710.76 # vsd lubos kai  pajamos virsija 43 vdu


            vsd = float(pajamos)* 0.63 * 0.0698
            if vsd <= lubos:
                self.langas.vsd_label.setText(str(round(vsd, 2)))
            else:
                self.langas.vsd_label.setText(str(lubos))

            # skaičiuojam privalomajį sveikatos draudimą
            psd = float(pajamos) * 0.63 * 0.1252
            self.langas.psd_label.setText(str(round(psd, 2)))

            # skaičiuojam gyventojų pajamų mokestį
            if apmokestinamos_pajamos < 20000:
                # pajamų mokesčio kreditas
                pmk = 0.1
                # gyvenotojų pajamų mokestis
                gpm = apmokestinamos_pajamos * 0.05 - pmk
            elif 20000 <= apmokestinamos_pajamos < 35000:
                pmk = apmokestinamos_pajamos * (0.1 - 2/300000 * (apmokestinamos_pajamos -20000))
                gpm = apmokestinamos_pajamos * 0.15 -pmk
            else:
                gpm = apmokestinamos_pajamos * 0.15

            self.langas.gpm_label.setText(str(round(gpm, 2)))

            # likutis
            likutis = round(float(pajamos) - gpm - vsd - psd, 2)
            self.langas.likutis_label.setText(str(likutis))

        else:
            tekstas = f'{metai} metais pajamų negauta.'
            self.langas.pajamos_label.setText(tekstas)
        pass
    
          

