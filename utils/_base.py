from exit import Ui_MainWindow
from Dialog_confirm import Ui_Dialog as Ui_Confirm
from Dialog_lineEdit import Ui_Dialog as Ui_lineEdit
from Dialog_comboBox import Ui_Dialog as Ui_comboBox

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QDialog, QTableView
from PyQt6.QtCore import QAbstractTableModel, Qt, QSettings, QRegularExpression
from PyQt6.QtGui import QShortcut, QKeySequence, QRegularExpressionValidator

import os, shutil, json
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

pd.set_option('future.no_silent_downcasting', True)


class pandasModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        QAbstractTableModel.__init__(self)
        
        self.init_data = data
        for col in data.columns:
            if is_datetime64_any_dtype(data[col]):
                data[col] = data[col].dt.strftime('%d-%b-%y')
        self._data = data.fillna('')
        
    def rowCount(self, parent=None): return self._data.shape[0]
    def columnCount(self, parnet=None): return self._data.shape[1]
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None
    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]
        return None

class Ui_plug:
    def __init__(self, string): a = string
    def exec(self): return 1


class Ui_Dialog_confirm(QDialog, Ui_Confirm):
    def __init__(self, string):
        QDialog.__init__(self)
        self.ui = uic.loadUi('Dialog_confirm.ui', self)
        diag_label = {
            'add': 'Подтвердите добавление строки',
            'edit': 'Подтвердите изменение строки',
            'delete': 'Подтвердите удаление строк',
            'delete_group': 'Подтвердите удаление группы',
            'delete_group_part': 'Подтвердите удаление строк'
        }
        self.label.setText(diag_label[string])
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button.setShortcut('enter')
        self.cancel_button.setShortcut('escape')
        
        settings = QSettings("MyCompany", "MyApp")
        sr = settings.value('string_to_delete')
        self.label_2.setText(self.insert_newline(self.combine_ranges(sr)))
    def insert_newline(self, text: list[str], max_chars=90) -> str:
        words = text  # Разбиваем строку на слова
        result = []
        current_line = []
        current_length = 0
        for word in words:
            if current_length + len(word) + len(', ') <= max_chars:
                current_line.append(word)
                current_length += len(word) + len(', ')
            else:
                result.append(', '.join(current_line))
                current_line = [word]
                current_length = len(word) + len(', ')
        if current_line:
            result.append(', '.join(current_line))
        if len(result) > 8:
            result = result[:8] + ['...']
        return ',\n'.join(result)
    def combine_ranges(self, numbers: list[int]):
        numbers = list(map(int, numbers))
        ranges = []
        start = numbers[0]
        end = start
        for i in range(1, len(numbers)):
            if numbers[i] == end + 1:
                end = numbers[i]
            else:
                ranges.append(str(start) if start == end else f"{start}-{end}")
                start = numbers[i]
                end = start
        ranges.append(str(start) if start == end else f"{start}-{end}")
        return ranges


class Ui_Dialog_lineEdit(QDialog, Ui_lineEdit):
    def __init__(self, string):
        QDialog.__init__(self)
        self.ui = uic.loadUi('Dialog_lineEdit.ui', self)
        diag_label = {
            'new_group': 'Создать группу',
            'save_group': 'Сохранить группу'
        }
        self.confirm_button.setText(diag_label[string])
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button.setShortcut('enter')
        self.cancel_button.setShortcut('escape')
        
        self.flag = True
        self.style_ = """background-color: rgb(255, 255, 255);font: 12pt "Segoe UI";"""
        self.name_lineEdit.setStyleSheet(self.style_)
        
        self.accepted.connect(self.on_close)
        self.name_lineEdit.textChanged.connect(self.check_name)
        
        self.check_name(group_name=None)
        
        settings = QSettings("MyCompany", "MyApp")
        sr = settings.value('string_to_group')
        self.label_2.setText(self.insert_newline(self.combine_ranges(sr)))
    def insert_newline(self, text: list[str], max_chars=90) -> str:
        words = text  # Разбиваем строку на слова
        result = []
        current_line = []
        current_length = 0
        for word in words:
            if current_length + len(word) + len(', ') <= max_chars:
                current_line.append(word)
                current_length += len(word) + len(', ')
            else:
                result.append(', '.join(current_line))
                current_line = [word]
                current_length = len(word) + len(', ')
        if current_line:
            result.append(', '.join(current_line))
        if len(result) > 8:
            result = result[:8] + ['...']
        return ',\n'.join(result)
    def combine_ranges(self, numbers: list[int]):
        numbers = list(map(int, numbers))
        ranges = []
        start = numbers[0]
        end = start
        for i in range(1, len(numbers)):
            if numbers[i] == end + 1:
                end = numbers[i]
            else:
                ranges.append(str(start) if start == end else f"{start}-{end}")
                start = numbers[i]
                end = start
        ranges.append(str(start) if start == end else f"{start}-{end}")
        return ranges
    def on_close(self):
        # Читаем значения из объектов диалога
        settings = QSettings("MyCompany", "MyApp")
        settings.setValue("name_lineEdit", self.name_lineEdit.text()) # Сохраняем значение
    def check_name(self, group_name):
        # Инициализация
        if group_name is None:
            self.confirm_button.clicked.disconnect()
            self.name_lineEdit.setStyleSheet(self.style_) 
            self.flag = False
            return
        # Определение наличие дубликатов
        self.flag_new = True 
        file_path = os.path.join('.', 'groups', 'names.txt')
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if group_name.strip() == ','.join(line.split(',')[1:]).strip():
                        self.flag_new = False           
        if not self.flag and self.flag_new:
            self.confirm_button.clicked.connect(self.accept)
            self.name_lineEdit.setStyleSheet(self.style_)
            self.flag = True
        elif (self.flag and not self.flag_new) or (self.name_lineEdit.text() == ''):
            self.confirm_button.clicked.disconnect()
            self.name_lineEdit.setStyleSheet(self.style_ + 'border: 1px solid red;') 
            self.flag = False


class Ui_Dialog_comboBox(QDialog, Ui_comboBox):
    def __init__(self, string):
        QDialog.__init__(self)
        self.ui = uic.loadUi('Dialog_comboBox.ui', self)
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button.setShortcut('enter')
        self.cancel_button.setShortcut('escape')
        self.choose_comboBox.currentTextChanged.connect(self.show_picked_group)
        
        self.choose_comboBox.clear()
        self.choose_comboBox.addItems([''] + self.list_of_groups())

        # Подключаем сигнал rejected к слоту
        self.accepted.connect(self.on_close)
    def on_close(self):
        # Читаем значения из объектов диалога
        settings = QSettings("MyCompany", "MyApp")
        settings.setValue("choose_comboBox", self.choose_comboBox.currentText()) # Сохраняем значение
    def list_of_groups(self) -> list:
        name_group_list = list()
        file_path = os.path.join('.', 'groups', 'names.txt')
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                name_group_list = [','.join(line.split(',')[1:]).strip() for line in f]
        # # Исключить из списка уже отображаемую группу
        # if self.stackedWidget.currentWidget() == self.page:
        #     name_group_list.remove(self.choose_comboBox.currentText())
        return name_group_list
    def show_picked_group(self, group_name: str):
        if self.choose_comboBox.currentText() == '':
            self.init_table.setModel(pandasModel(pd.DataFrame()))
            return
        file_path = os.path.join('.', 'groups', 'names.txt')
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if group_name == ','.join(line.split(',')[1:]).strip():
                        file_name = line.split(',')[0]
                        break
        params = {'dtype': { 'kod': 'int16', 'take_part': 'int8'}, 'parse_dates': [9], 'date_format': '%d-%b-%y'}
        df = pd.read_csv(file_name, **params).sort_values(by='Номер', axis=0, ascending=True)
        self.init_table.setModel(pandasModel(df))
        self.init_table.resizeColumnsToContents()
        # Укорачивание столбца Расшифровка
        for id, col in enumerate(self.init_table.model().init_data.columns):
            if col == 'Расшифровка':
                self.init_table.setColumnWidth(id, 487); break




class Base_Class(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = uic.loadUi('exit.ui', self) 
        # Загружаем все данные в формате pd.DataFrame
        # self.df_ntp, self.df_reg, self.df_grnti = self.load_data('data')
        self.df_ntp, self.df_reg, self.df_grnti = self.load_data2('data', 'temp_data')
        # Записываем переменные
        self.settings_dict = self.get_settings()
        self.cur_name: str = 'empty'
        self.regex_grnti = r'^(?:\d{2}(\.(\d{2}(\.(\d{2})?)?)?)?)$'
        self.regex_grntis = r'(?:^\d{2}(\.(\d{2}(\.(\d{2})?)?)?)?(\,\s\d{2}(\.(\d{2}(\.(\d{2})?)?)?)?)?)$'
        self.regex_name = r'^(?:[А-ЯЁа-яё]+)(?:\s([А-ЯЁа-яё]+|[А-ЯЁа-яё]\.)((\s[А-ЯЁа-яё]+|\s?[А-ЯЁа-яё]\.))?)?$'
        # Валидаторы
        self.validator_grnti = QRegularExpressionValidator(QRegularExpression(r'^(?:[\d\.]{2,8})$'))
        self.validator_name = QRegularExpressionValidator(QRegularExpression(r'^(?:[А-ЯЁа-яё\.\s]+)$'))
        self.validator_name_edit = QRegularExpressionValidator(QRegularExpression(r'^(?:[А-ЯЁа-яё\.\s]+)$'))
        self.validator_multi = QRegularExpressionValidator(QRegularExpression(r'^(?:[А-ЯЁа-яё\.\s\,]+)$'))
        # Сохранение данные
        self.save_abc(dir_name='temp_data', dfs=('df_ntp','df_reg','df_grnti'))
        # При закрытии приложения
        self.closeEvent = self.on_close_event
    
    
    def app_exit(self) -> None: 
        self.save_abc(dir_name='temp_data', dfs=('df_ntp','df_reg','df_grnti'))
        exit()
    def on_close_event(self, event):
        self.save_abc(dir_name='temp_data', dfs=('df_ntp','df_reg','df_grnti'))
        event.accept()
    def recover_data(self):
        # Удаляяем папку temp_data 
        if os.path.isdir(os.path.join('.', 'temp_data')):
            shutil.rmtree(os.path.join('.', 'temp_data')) 
        # Удаляяем папку с группами
        if os.path.isdir(os.path.join('.', 'groups')):
            shutil.rmtree(os.path.join('.', 'groups'))
        self.df_ntp, self.df_reg, self.df_grnti = self.load_data('data')
        # Отображение "Эксперты НТП"
        self.settings_dict = self.get_settings()
        self.show_table('ntp')
    def open_dialog(self, string):
        pass
        
    def start_position(self, btns: bool = False) -> None:
        self.stackedWidget.setCurrentWidget(self.page_1)
        self.help_widget.setHidden(True)
        self.addexpert_widget.setHidden(True)
        self.edit_widget.setHidden(True)
        self.filter_widget.setHidden(True)
        self.add_widget.setHidden(btns)
        self.ramka1.setHidden(btns)
        self.ramka2.setHidden(btns)
        self.ramka3.setHidden(btns)
        self.filterlist_name.setHidden(True)
            
        
    def btn_connect(self) -> None:
        # Меню
        self.ntp_show.triggered.connect(lambda: self.show_table('ntp'))
        self.reg_show.triggered.connect(lambda: self.show_table('reg'))
        self.grnti_show.triggered.connect(lambda: self.show_table('grnti'))
        self.load_group.triggered.connect(lambda: self.open_dialog('choose_group'))
        self.save_group.triggered.connect(lambda: self.open_dialog('new_group'))
        self.delete_group.triggered.connect(lambda: self.open_dialog('delete_group'))
        self.hotkeys_show.triggered.connect(lambda: self.help_widget.setHidden(False))
        self.recover.triggered.connect(self.recover_data)
        # Главные кнопки
        self.add_button.clicked.connect(lambda: self.show_add_widget(False))
        self.delete_button.clicked.connect(lambda: self.open_dialog('delete'))
        self.edit_button.clicked.connect(lambda: self.show_edit_widget(False))
        self.add_expert_button.clicked.connect(lambda: self.open_dialog('new_group'))
        self.filter_button.clicked.connect(lambda: self.show_filter_widget(False))
        self.filter_button_2.clicked.connect(lambda: self.select_all_rows(True))
        self.filter_button_3.clicked.connect(lambda: self.select_all_rows(False))
        # Фильтр
        self.filter_close_button.clicked.connect(lambda: self.show_filter_widget(True))
        self.filter_apply_button.clicked.connect(self.apply_filter_widget)
        self.filter_reset_button.clicked.connect(self.reset_filter_widget)
        # Добавить
        self.addexpert_close_button.clicked.connect(lambda: self.show_add_widget(True))
        self.addexpert_apply_button.clicked.connect(lambda: self.open_dialog('add'))
        self.addexpert_reset_button.clicked.connect(self.reset_add_widget)
        # Редактировать
        self.edit_close_button.clicked.connect(lambda: self.show_edit_widget(True))
        self.edit_apply_button.clicked.connect(lambda: self.open_dialog('edit'))
        self.edit_reset_button.clicked.connect(lambda: self.show_edit_widget(False))
        # Помощь
        self.help_close_button_3.clicked.connect(lambda: self.help_widget.setHidden(True))
        # Работа с экспертными группами
        self.edit_group_button.clicked.connect(lambda: self.open_dialog('delete_group_part'))
        self.approve_group_button.clicked.connect(self.approve_group_final)
        self.add_group_button.clicked.connect(lambda: self.open_dialog('merge_group'))
        self.importExcel_group_button.clicked.connect(self.save_to_excel)
        
    
    
    def keyboard_connect(self) -> None:
        # Меню
        self.ntp_show.setShortcut('Ctrl+1')
        self.reg_show.setShortcut('Ctrl+2')
        self.grnti_show.setShortcut('Ctrl+3')
        self.load_group.setShortcut('Ctrl+4')
        self.save_group.setShortcut('Ctrl+5')
        self.delete_group.setShortcut('Ctrl+6')
        # Close widgets
        self.filter_close_button.setShortcut('escape')
        self.addexpert_close_button.setShortcut('escape')
        self.edit_close_button.setShortcut('escape')
        # Удалить экспертов
        self.delete_button.setShortcut('backspace')
        self.filter_button.setShortcut('f')
        # Закрытие приложения
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.app_exit)
    
    
    def layers(self) -> None:
        self.init_table.raise_()
        self.init_tablename.raise_()
        self.ramka1.lower()
        self.ramka2.lower()
        self.add_widget.lower()
        self.addexpert_widget.raise_()
        self.edit_widget.raise_()
        self.filter_widget.raise_()
        self.help_widget.raise_()
    
    
    def get_settings(self) -> dict:
        return  {
            'ntp': {
                'df': self.df_ntp,
                'mode': QTableView.SelectionMode.ExtendedSelection,
                'behave': QTableView.SelectionBehavior.SelectRows,
                'label': 'Эксперты НТП'
            },
            'reg': {
                'df': self.df_reg,
                'mode': QTableView.SelectionMode.ExtendedSelection,
                'behave': QTableView.SelectionBehavior.SelectItems,
                'label': 'Справочник по регионам'
            },
            'grnti': {
                'df': self.df_grnti,
                'mode': QTableView.SelectionMode.ExtendedSelection,
                'behave': QTableView.SelectionBehavior.SelectItems,
                'label': 'Код рубрики (ГРНТИ)'
            }
        }


    def save_abc(self, dir_name: str, dfs: tuple[str]):
        if not os.path.isdir(os.path.join('.', dir_name)):
            os.mkdir(os.path.join('.', dir_name))
        
        params_all = {'index': False, 'encoding': "utf-8", 'date_format': '%d-%b-%y', 'sep':';'}
        for name in dfs:
            getattr(self, f'{name}').to_csv(os.path.join('.', dir_name, f'{name}.csv'), **params_all)
    
    
    def load_data(self, dir_name: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        if not os.path.isdir(os.path.join('.', dir_name)):
            print(f'Нет папки {dir_name} с данными')
            return
        # Загружаем данные
        params = {'dtype': { 'Номер': 'int16', 'Участие': 'int8'}, 'parse_dates': [7], 'date_format': '%d-%b-%y'}
        
        df_ntp = pd.read_csv(os.path.join('.', dir_name, 'Expert.csv'), **params)
        # df_reg = pd.read_csv(os.path.join('.', dir_name, 'Reg_obl_city.csv'), delimiter=';')
        df_reg = pd.read_csv(os.path.join('.', dir_name, 'russian_cities.csv'), delimiter=';')
        # df_grnti = pd.read_csv(os.path.join('.', dir_name, 'grntirub.csv'))
        df_grnti = pd.read_csv(os.path.join('.', dir_name, 'grnti-latest.csv'), header=0, usecols=[0,1], names=['Код', 'Расшифровка']).drop_duplicates(keep='first')
        
        # Title case GRNTI
        # df_grnti['Расшифровка'] = df_grnti['Расшифровка'].str.capitalize()
        
        # Расшифровка
        dtypes_grnti = {'level_0_code': str, 'level_1_code': str, 'level_2_code': str, 'level_0_title': str, 'level_1_title': str, 'level_2_title': str}
        df_grnti_all = pd.read_csv(os.path.join('.', dir_name, 'grnti-latest.csv'), dtype=dtypes_grnti)
        dict1 = {k:v for k,v in zip(df_grnti_all.level_0_code.tolist(), df_grnti_all.level_0_title.tolist()) if k != ''}
        dict2 = {k:v for k,v in zip(df_grnti_all.level_1_code.tolist(), df_grnti_all.level_1_title.tolist()) if k != ''}
        dict3 = {k:v for k,v in zip(df_grnti_all.level_2_code.tolist(), df_grnti_all.level_2_title.tolist()) if k != ''}
        self.dict_grnti = dict1 | dict2 | dict3
        df_ntp['Расшифровка'] = df_ntp['ГРНТИ'].str.split(r', ').map(lambda num: ', '.join(dict.fromkeys([a for n in num if (a := self.dict_grnti.get(n, ''))])))
        
        if not os.path.isfile(os.path.join('.', 'data', 'dict_grnti.json')):
            # Сохранение словаря в файл
            with open(os.path.join('.', 'data', 'dict_grnti.json'), 'w') as f:
                json.dump(self.dict_grnti, f)
        
        # Регион
        # TODO: Кастыль
        self.dict_reg = {k:v for k,v in zip(df_reg['Город'].tolist(), df_reg['Регион'].tolist())} 
        df_ntp = pd.merge(df_ntp, df_reg.drop('Округ', axis=1), how='left', on='Город')
        # Округ
        df_ntp = pd.merge(df_ntp.drop('Округ', axis=1), df_reg.drop('Регион', axis=1), how='left', on='Город')
        df_ntp = df_ntp[['Номер', 'ФИО', 'Округ', 'Регион', 'Город', 'ГРНТИ', 'Расшифровка', 'Ключевые слова', 'Участие', 'Дата добавления']]
        
        return df_ntp, df_reg, df_grnti


    def load_data2(self, dir_name: str, dir_name2: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        if not os.path.isdir(os.path.join('.', dir_name2)):
            print(f'Нет папки {dir_name2} с данными')
            print(f'Попытка загрузить данные из папки {dir_name}')
            return self.load_data(dir_name)
        # Загружаем данные
        params_ntp = {'dtype': { 'Номер': 'int16', 'Участие': 'int8'}, 'parse_dates': [9]}
        params_all = {'encoding': "utf-8", 'date_format': '%d-%b-%y', 'delimiter': ';'}
        
        df_ntp = pd.read_csv(os.path.join('.', dir_name2, 'df_ntp.csv'), **params_ntp, **params_all)
        df_reg = pd.read_csv(os.path.join('.', dir_name2, 'df_reg.csv'), **params_all)
        df_grnti = pd.read_csv(os.path.join('.', dir_name2, 'df_grnti.csv'), **params_all)
        
        # Чтение словаря из файла
        with open(os.path.join('.', 'data', 'dict_grnti.json'), 'r') as f:
            self.dict_grnti = json.load(f)
        
        return df_ntp, df_reg, df_grnti