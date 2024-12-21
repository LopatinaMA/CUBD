from utils._base import Base_Class, pandasModel
from utils._edit import Edit_Row

from PyQt6.QtCore import QTimer

import re

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype


class Add_Row(Base_Class):
    
    def __init__(self):
        # Placeholder
        self.addexpert_name_lineEdit.setPlaceholderText('Формат: Иванов И.И.')
        self.addexpert_grnti_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.addexpert_grnti2_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.addexpert_keywords_lineEdit.setPlaceholderText('Введите ключевые слова через запятую:')
        # Валидация
        self.addexpert_name_lineEdit.setValidator(self.validator_name)
        self.addexpert_grnti_lineEdit.setValidator(self.validator_grnti)
        self.addexpert_grnti2_lineEdit.setValidator(self.validator_grnti)
        self.addexpert_keywords_lineEdit.setValidator(self.validator_multi)
        self.addexpert_city_comboBox.setEditable(True)
        # Заполнение CheckBox
        self.connect_on_off_add(True)
        self.fill_add_comboBox()
        # Скрыть ошибку
        self.warning_addexpert_label.setHidden(True)
        self.addexpert_grnti_lineEdit.textChanged.connect(lambda x: Edit_Row.grnti_number_compliter(self, x, 'addexpert_grnti_lineEdit'))
        self.addexpert_grnti2_lineEdit.textChanged.connect(lambda x: Edit_Row.grnti_number_compliter(self, x, 'addexpert_grnti2_lineEdit'))
        
    
    def fill_add_comboBox(self, comdict: dict | None = None):
        # Временно отключаем сигнал currentIndexChanged
        self.connect_on_off_add(False)
        
        self.addexpert_reg_comboBox.clear()
        self.addexpert_region_comboBox.clear()
        self.addexpert_city_comboBox.clear()

        if comdict is None:
            self.addexpert_reg_comboBox.addItems([''] + sorted(self.df_reg['Округ'].unique()))
            self.addexpert_region_comboBox.addItems([''] + sorted(self.df_reg['Регион'].unique()))
            self.addexpert_city_comboBox.addItems([''] + sorted(self.df_reg['Город'].unique()))
        else:
            self.addexpert_reg_comboBox.addItems([''] + comdict['reg_list'])
            self.addexpert_region_comboBox.addItems([''] + comdict['region_list'])
            self.addexpert_city_comboBox.addItems([''] + comdict['city_list'])
            
            self.addexpert_reg_comboBox.setCurrentText(comdict['reg_main'])
            self.addexpert_region_comboBox.setCurrentText(comdict['region_main'])
            self.addexpert_city_comboBox.setCurrentText(comdict['city_main'])
        # Временно отключаем сигнал currentIndexChanged
        self.connect_on_off_add(True)
    
    
    def update_add_cB(self, colname: str, widget_: str):
        dict_cB = Edit_Row.get_less_list(self, colname, widget_)
        self.fill_add_comboBox(dict_cB)
    
    
    def connect_on_off_add(self, flag: bool = True):
        if flag:
            self.addexpert_reg_comboBox.currentIndexChanged.connect(lambda: self.update_add_cB('Округ', 'addexpert_reg_comboBox'))
            self.addexpert_region_comboBox.currentIndexChanged.connect(lambda: self.update_add_cB('Регион', 'addexpert_region_comboBox'))
            self.addexpert_city_comboBox.currentIndexChanged.connect(lambda: self.update_add_cB('Город', 'addexpert_city_comboBox'))
        else:
            self.addexpert_reg_comboBox.currentIndexChanged.disconnect()
            self.addexpert_region_comboBox.currentIndexChanged.disconnect()
            self.addexpert_city_comboBox.currentIndexChanged.disconnect()
    
        
    def apply_add_widget(self) -> None:
        new_row = self.get_row_add_widget()
        self.add_row(new_row)
        
        
    def before_add_widget(self):
        if not self.stackedWidget.currentWidget() == self.page_1:
            return False
        return self.checkers_add_widget()
    
    
    def show_add_widget(self, hide: bool) -> None:
        self.reset_style_addexpert()
        self.reset_add_widget()
        self.addexpert_widget.setHidden(hide)
            
    
    def get_row_add_widget(self) -> pd.DataFrame:
        # Формирование ГРНТИ
        grntis = sorted((str(self.addexpert_grnti_lineEdit.text().rstrip('.')), str(self.addexpert_grnti2_lineEdit.text().rstrip('.'))))
        str_grntis = ''
        for item in grntis:
            if item:
                if str_grntis: str_grntis += ', '
            str_grntis += item
            
        # ['Номер', 'ФИО', 'Округ', "Регион", 'Город', 'ГРНТИ', "Расшифровка", 'Ключевые слова', 'Участие', 'Дата добавления']
        new_row = pd.Series([
            self.df_ntp['Номер'].max()+1,
            self.addexpert_name_lineEdit.text(),
            self.addexpert_reg_comboBox.currentText(),
            self.addexpert_region_comboBox.currentText(),
            self.addexpert_city_comboBox.currentText(),
            str_grntis,
            ', '.join(dict.fromkeys([raschif for num in grntis if (raschif := self.dict_grnti.get(num, ''))])),
            self.addexpert_keywords_lineEdit.text(),
            0,
            pd.Timestamp.today().strftime('%d-%b-%y')
        ],
        index=self.settings_dict[self.cur_name]['df'].columns
        )
        new_row = new_row.to_frame().T
        for col in new_row.columns:
            if is_datetime64_any_dtype(new_row[col]):
                new_row[col] = new_row[col].dt.strftime('%d-%b-%y')
        return new_row
    
        
    def add_row(self, row: pd.DataFrame) -> None:        
        self.settings_dict[self.cur_name]['df'] = pd.concat([self.settings_dict[self.cur_name]['df'], row], ignore_index=True)
        self.settings_dict[self.cur_name]['df'] = self.settings_dict[self.cur_name]['df'].astype(self.settings_dict[self.cur_name]['df'].dtypes)
        self.df_ntp = pd.concat([self.df_ntp, row], ignore_index=True)
        self.df_ntp = self.df_ntp.astype(self.df_ntp.dtypes)
        self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        
        if self.df_reg[self.df_reg['Город'] == row["Город"].at[0]].empty:
            self.df_reg = pd.concat([self.df_reg, row[['Округ', 'Регион', 'Город']]], ignore_index=True)
            self.settings_dict['reg']['df'] = self.df_reg
        
        self.init_table.scrollToBottom()
        self.init_table.selectRow(self.settings_dict[self.cur_name]['df'].index.max())
        self.reset_add_widget()
        self.addexpert_widget.setHidden(True)
    
    
    def checkers_add_widget(self) -> bool:
        new_row = self.get_row_add_widget()
        
        def is_unique_row(row: pd.Series) -> bool:
            query_string = r'`ФИО` == @row["ФИО"] and `Город` == @row["Город"] and `ГРНТИ` == @row["ГРНТИ"]'
            return not self.df_ntp.query(query_string).empty
        def is_empty_filed(row: pd.Series) -> bool:
            return (~row.loc[['ФИО', 'Округ', 'Регион', 'Город', 'ГРНТИ']].astype(bool)).sum()
        def regex_correct_grnti(row: pd.Series) -> bool:
            return not bool(re.match(self.regex_grntis, new_row.at[0, 'ГРНТИ']))
        def regex_correct_fio(row: pd.Series) -> bool:
            return not bool(re.match(self.regex_name, new_row.at[0, 'ФИО']))
        
        if is_unique_row(new_row.iloc[0]):
            self.warning_addexpert_label.setText("Такой эксперт уже добавлен")
            self.warning_addexpert_label.setHidden(False)
            QTimer.singleShot(5000, lambda: self.warning_addexpert_label.setHidden(True))
            return False
        if is_empty_filed(new_row.iloc[0]):
            self.reset_style_addexpert()
            if self.addexpert_name_lineEdit.text() == '':
                self.addexpert_name_lineEdit.setStyleSheet("border: 1px solid red;")
            if self.addexpert_grnti_lineEdit.text() == '' and self.addexpert_grnti2_lineEdit.text() == '':
                for i in ['grnti', 'grnti2']: getattr(self, f'addexpert_{i}_lineEdit').setStyleSheet("border: 1px solid red;")
            for i in ['reg', 'region', 'city']:
                if getattr(self, f'addexpert_{i}_comboBox').currentText() == '':
                    getattr(self, f'addexpert_{i}_comboBox').setStyleSheet("border: 1px solid red;")
            return False
        if regex_correct_grnti(new_row.iloc[0]):
            self.warning_addexpert_label.setText("Некорректный формат ГРНТИ!")
            self.warning_addexpert_label.setHidden(False)
            QTimer.singleShot(5000, lambda: self.warning_addexpert_label.setHidden(True))
            return False
        if regex_correct_fio(new_row.iloc[0]):
            self.warning_addexpert_label.setText("Некорректный формат ФИО!")
            self.warning_addexpert_label.setHidden(False)
            QTimer.singleShot(5000, lambda: self.warning_addexpert_label.setHidden(True))
            return False
        
        return True


    def reset_style_addexpert(self) -> None:
        a = 'background-color: rgb(255,255,255);font: 12pt "Segoe UI";border-style: solid;border-width: 1px;border-color: rgb(220, 220, 220);border-radius: 7px;'
        self.addexpert_name_lineEdit.setStyleSheet(a)
        self.addexpert_reg_comboBox.setStyleSheet(a)
        self.addexpert_region_comboBox.setStyleSheet(a)
        self.addexpert_city_comboBox.setStyleSheet(a)
        self.addexpert_grnti_lineEdit.setStyleSheet(a)
        self.addexpert_grnti2_lineEdit.setStyleSheet(a)
        self.addexpert_keywords_lineEdit.setStyleSheet(a)


    def reset_add_widget(self) -> None:
        self.addexpert_name_lineEdit.setText('')
        self.addexpert_reg_comboBox.setCurrentText('')
        self.addexpert_region_comboBox.setCurrentText('')
        self.addexpert_city_comboBox.setCurrentText('')
        self.addexpert_grnti_lineEdit.setText('')
        self.addexpert_grnti2_lineEdit.setText('')
        self.addexpert_keywords_lineEdit.setText('')

        self.warning_addexpert_label.setHidden(True)