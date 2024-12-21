from utils._base import Base_Class, pandasModel

from PyQt6.QtWidgets import QTableView
from PyQt6.QtCore import QTimer

import pandas as pd
import re

class Edit_Row(Base_Class):
    
    def __init__(self):
        # Placeholder
        self.edit_name_lineEdit.setPlaceholderText('ФИО эксперта')
        self.edit_grnti_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.edit_grnti2_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.edit_keywords_lineEdit.setPlaceholderText('Ключевые слова через запятую:')
        # Валидация
        self.edit_name_lineEdit.setValidator(self.validator_name_edit)
        self.edit_grnti_lineEdit.setValidator(self.validator_grnti)
        self.edit_grnti2_lineEdit.setValidator(self.validator_grnti)
        self.edit_keywords_lineEdit.setValidator(self.validator_multi)
        self.edit_city_comboBox.setEditable(True)
        # Предупреждения
        self.warning_edit_label.setHidden(True)
        self.warning_editwidget_label.setHidden(True)
        # При изменении значения в checkBox
        self.connect_on_off_edit(True)
        self.edit_grnti_lineEdit.textChanged.connect(lambda x: self.grnti_number_compliter(x, 'edit_grnti_lineEdit'))
        self.edit_grnti2_lineEdit.textChanged.connect(lambda x: self.grnti_number_compliter(x, 'edit_grnti2_lineEdit'))
        a = 'background-color: rgb(255,255,255);font: 12pt "Segoe UI";font-weight: 250;'
        self.edit_city_comboBox.setStyleSheet(a)

    def grnti_number_compliter(self, text: str, widget_: str):
        # Удаляем пробелы и нецифровые символы
        text = ''.join(c for c in text if c.isdigit())

        # Добавляем точки после каждой второй цифры
        parts = [text[i:i+2] for i in range(0, len(text), 2)]
        formatted_text = '.'.join(parts)

        # Ограничиваем максимальную длину
        if len(formatted_text) > 8: # 6 цифр + 2 точки
            formatted_text = formatted_text[:8] 

        # Устанавливаем отформатированный текст в QLineEdit
        getattr(self, widget_).setText(formatted_text)
    
    def show_edit_widget(self, hide: bool) -> None:
        if not hide and len(sr := self.rows_selected()) != 1:
            self.warning_edit_label.setHidden(False)
            QTimer.singleShot(3000, lambda: self.warning_edit_label.setHidden(True))
            return
        elif hide:
            self.edit_widget.setHidden(hide)
            self.reset_edit_widget()
            self.init_table.setSelectionMode(self.settings_dict[self.cur_name]['mode'])
        else:
            self.warning_edit_label.setHidden(True)
            old_row = self.init_table.model().init_data.iloc[sr[0], :].fillna('')
            self.init_table.setSelectionMode(QTableView.SelectionMode.NoSelection)
            self.edit_city_comboBox.setCurrentText(old_row['Город'])
            self.update_edit_cB('Город', 'edit_city_comboBox')
            self.fill_edit_widget(old_row)
            self.edit_widget.setHidden(hide)


    def fill_edit_comboBox(self, comdict: dict | None = None):
        # Временно отключаем сигнал currentIndexChanged
        self.connect_on_off_edit(False)
        
        self.edit_reg_comboBox.clear()
        self.edit_region_comboBox.clear()
        self.edit_city_comboBox.clear()
        
        if comdict is None:
            self.edit_reg_comboBox.addItems([''] + sorted(self.df_reg['Округ'].unique()))
            self.edit_region_comboBox.addItems([''] + sorted(self.df_reg['Регион'].unique()))
            self.edit_city_comboBox.addItems([''] + sorted(self.df_reg['Город'].unique()))
        else:
            self.edit_reg_comboBox.addItems([''] + comdict['reg_list'])
            self.edit_region_comboBox.addItems([''] + comdict['region_list'])
            self.edit_city_comboBox.addItems([''] + comdict['city_list'])
            
            self.edit_reg_comboBox.setCurrentText(comdict['reg_main'])
            self.edit_region_comboBox.setCurrentText(comdict['region_main'])
            self.edit_city_comboBox.setCurrentText(comdict['city_main'])
        # Временно отключаем сигнал currentIndexChanged
        self.connect_on_off_edit(True)
            
    
    def fill_edit_widget(self, row: pd.Series) -> None:
        # 'ФИО', 'Округ', 'Город', 'ГРНТИ', 'ГРНТИ', 'Ключевые слова'
        # Временно отключаем сигнал currentIndexChanged
        self.connect_on_off_edit(False)
        self.edit_name_lineEdit.setText(row['ФИО'])
        self.edit_reg_comboBox.setCurrentText(row['Округ'])
        self.edit_region_comboBox.setCurrentText(row['Регион'])
        self.edit_city_comboBox.setCurrentText(row['Город'])
        self.edit_grnti_lineEdit.setText(row['ГРНТИ'].split(', ')[0])
        if len(row['ГРНТИ'].split(', ')) > 1:
            self.edit_grnti2_lineEdit.setText(row['ГРНТИ'].split(', ')[1])
        else:
            self.edit_grnti2_lineEdit.setText('')
        self.edit_keywords_lineEdit.setText(row['Ключевые слова'])
        # Временно отключаем сигнал currentIndexChanged
        self.connect_on_off_edit(True)
    
    
    def get_less_list(self, colname: str, widget_: str) -> dict:
        colvalue = getattr(self, widget_).currentText()
        
        reg_main    = colvalue if colname == 'Округ' else ''
        region_main = colvalue if colname == 'Регион' else ''
        city_main   = colvalue if colname == 'Город' else ''
        
        if (reg_main, region_main, city_main) == ('','',''):
            return {
            'reg_main'      : reg_main,
            'region_main'   : region_main,
            'city_main'     : city_main,
            'reg_list'      : sorted(self.df_reg['Округ'].unique()),
            'region_list'   : sorted(self.df_reg['Регион'].unique()),
            'city_list'     : sorted(self.df_reg['Город'].unique())
        }

        match colname:
            case 'Округ':
                city_list   = sorted(self.df_reg.query('`Округ` == @reg_main')['Город'].unique())
            case 'Регион':
                reg_main    = self.df_reg.query(f'`{colname}` == @region_main')['Округ'].iat[0]
                city_list   = sorted(self.df_reg.query('`Регион` == @region_main')['Город'].unique())
            case 'Город':
                reg_main    = self.df_reg.query(f'`{colname}` == @city_main')['Округ'].iat[0]
                region_main = self.df_reg.query(f'`{colname}` == @city_main')['Регион'].iat[0]
                city_list   = sorted(self.df_reg.query('`Регион` == @region_main')['Город'].unique())
        return {
            'reg_main'      : reg_main,
            'region_main'   : region_main,
            'city_main'     : city_main,
            'reg_list'      : sorted(self.df_reg['Округ'].unique()),
            'region_list'   : sorted(self.df_reg.query('`Округ` == @reg_main')['Регион'].unique()),
            'city_list'     : city_list
        }
    
    
    def update_edit_cB(self, colname: str, widget_: str):
        dict_cB = self.get_less_list(colname, widget_)
        self.fill_edit_comboBox(dict_cB)
    
    
    def connect_on_off_edit(self, flag: bool = True):
        if flag:
            self.edit_reg_comboBox.currentIndexChanged.connect(lambda: self.update_edit_cB('Округ', 'edit_reg_comboBox'))
            self.edit_region_comboBox.currentIndexChanged.connect(lambda: self.update_edit_cB('Регион', 'edit_region_comboBox'))
            self.edit_city_comboBox.currentIndexChanged.connect(lambda: self.update_edit_cB('Город', 'edit_city_comboBox'))
        else:
            self.edit_reg_comboBox.currentIndexChanged.disconnect()
            self.edit_region_comboBox.currentIndexChanged.disconnect()
            self.edit_city_comboBox.currentIndexChanged.disconnect()
    
    
    def get_edit_row(self):
        # ['Номер', 'ФИО', 'Округ', 'Город', 'ГРНТИ', 'Ключевые слова', 'Участие', 'Дата добавления']
        sr = self.rows_selected()
        old_row = self.init_table.model().init_data.iloc[sr[0], :]
        
        # Формирование ГРНТИ
        grntis = sorted((str(self.edit_grnti_lineEdit.text().rstrip('.')), str(self.edit_grnti2_lineEdit.text().rstrip('.'))))
        str_grntis = ''
        for item in grntis:
            if item:
                if str_grntis: str_grntis += ', '
            str_grntis += item
        
        new_row = pd.Series([
            old_row['Номер'],
            self.edit_name_lineEdit.text(),
            self.edit_reg_comboBox.currentText(),
            self.edit_region_comboBox.currentText(),
            self.edit_city_comboBox.currentText(),
            str_grntis,
            ', '.join(dict.fromkeys([raschif for num in grntis if (raschif := self.dict_grnti.get(num, ''))])), 
            self.edit_keywords_lineEdit.text(),
            old_row['Участие'],
            old_row['Дата добавления']
        ], 
        index=old_row.index
        )
        return new_row
    
    
    def apply_edit_widget(self):
        self.warning_editwidget_label.setHidden(True)
        
        sr = self.rows_selected()
        old_row = self.init_table.model().init_data.iloc[sr[0], :]
        new_row = self.get_edit_row()
        
        id = self.df_ntp.query('`Номер` == @old_row["Номер"]').index.to_list()[0]
        self.settings_dict[self.cur_name]['df'].iloc[id, :] = new_row
        self.init_table.model().init_data.iloc[sr[0], :] = new_row
        
        self.init_table.setModel(pandasModel(self.init_table.model().init_data))
        self.edit_widget.setHidden(True)
        self.init_table.setSelectionMode(self.settings_dict[self.cur_name]['mode'])
                
        new_row = new_row.to_frame().T
        if self.df_reg[self.df_reg['Город'] == new_row["Город"].at[0]].empty:
            self.df_reg = pd.concat([self.df_reg, new_row[['Округ', 'Регион', 'Город']]], ignore_index=True)
            self.settings_dict['reg']['df'] = self.df_reg
        


    
    def rows_selected(self) -> list:
        return list(set(i.row() for i in self.init_table.selectedIndexes()))
    
    
    def before_edit_widget(self):
        if not self.stackedWidget.currentWidget() == self.page_1:
            return False
        new_row = self.get_edit_row()
        flags = self.varify_edding_row(new_row)
        if all(flags):
            self.warning_editwidget_label.setHidden(True)
            return True
        elif flags == (True, True, False):
            self.warning_editwidget_label.setText('Такой эксперт уже добавлен!')
            self.warning_editwidget_label.setHidden(False)
            QTimer.singleShot(3000, lambda: self.warning_editwidget_label.setHidden(True))
            return False
        elif flags == (True, False, True):
            self.warning_editwidget_label.setText('Заполните пустые поля!')
            self.warning_editwidget_label.setHidden(False)
            QTimer.singleShot(3000, lambda: self.warning_editwidget_label.setHidden(True))
            return False
        elif flags == (False, True, True):
            self.warning_editwidget_label.setText('Некорректный формат ГРНТИ!')
            self.warning_editwidget_label.setHidden(False)
            QTimer.singleShot(3000, lambda: self.warning_editwidget_label.setHidden(True))
            return False
    
    
    def varify_edding_row(self, row: pd.Series) -> tuple[bool,...]:        
        query_string = r'`ФИО` == @row["ФИО"] and `Город` == @row["Город"] and `ГРНТИ` == @row["ГРНТИ"] and `Ключевые слова` == @row["Ключевые слова"]'
        flag = (
            bool(re.match(self.regex_grntis, row['ГРНТИ'])),
            not (~row.loc[['ФИО', 'Округ', 'Регион', 'Город', 'ГРНТИ']].astype(bool)).sum(),
            self.df_ntp.query(query_string).empty
        )
        return flag
            
            
    def reset_edit_widget(self) -> None:
        # Временно отключаем сигнал currentIndexChanged
        self.connect_on_off_edit(False)
        self.edit_name_lineEdit.setText('')
        self.edit_reg_comboBox.setCurrentText('')
        self.edit_region_comboBox.setCurrentText('')
        self.edit_city_comboBox.setCurrentText('')
        self.edit_grnti_lineEdit.setText('')
        self.edit_grnti2_lineEdit.setText('')
        self.edit_keywords_lineEdit.setText('')
        # Временно отключаем сигнал currentIndexChanged
        self.connect_on_off_edit(True)