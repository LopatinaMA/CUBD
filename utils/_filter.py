from utils._base import Base_Class, pandasModel
from utils._edit import Edit_Row

class Filter_table(Base_Class):
    
    def __init__(self):
        # Placeholder
        self.filter_grnti_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.filter_grnti2_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.filter_keywords_lineEdit.setPlaceholderText('Введите ключевые слова через запятую:')
        # Валидация
        self.filter_grnti_lineEdit.setValidator(self.validator_grnti)
        self.filter_grnti2_lineEdit.setValidator(self.validator_grnti)
        self.filter_keywords_lineEdit.setValidator(self.validator_multi)
        # Заполнение CheckBox
        self.connect_on_off_filter(True)
        self.fill_filter_comboBox()
        
        self.filter_grnti_lineEdit.textChanged.connect(lambda x: Edit_Row.grnti_number_compliter(self, x, 'filter_grnti_lineEdit'))
        self.filter_grnti2_lineEdit.textChanged.connect(lambda x: Edit_Row.grnti_number_compliter(self, x, 'filter_grnti2_lineEdit'))

        
    
    def fill_filter_comboBox(self, comdict: dict | None = None):
        # Временно отключаем сигнал currentIndexChanged
        self.connect_on_off_filter(False)
        
        if comdict is None:
            f_reg_c = self.filter_reg_comboBox.currentText()
            f_region_c = self.filter_region_comboBox.currentText()
            f_city_c = self.filter_city_comboBox.currentText()
        f_takepart_c = self.filter_takepart_comboBox.currentText()
        
        self.filter_reg_comboBox.clear()
        self.filter_region_comboBox.clear()
        self.filter_city_comboBox.clear()
        self.filter_takepart_comboBox.clear()

        self.filter_takepart_comboBox.addItems([''] + sorted(map(str, self.df_ntp['Участие'].unique())))
        
        if comdict is None:
            self.filter_reg_comboBox.addItems([''] + sorted(self.df_reg['Округ'].unique()))
            self.filter_region_comboBox.addItems([''] + sorted(self.df_reg['Регион'].unique()))
            self.filter_city_comboBox.addItems([''] + sorted(self.df_reg['Город'].unique()))
            
            self.filter_reg_comboBox.setCurrentText(f_reg_c)
            self.filter_region_comboBox.setCurrentText(f_region_c)
            self.filter_city_comboBox.setCurrentText(f_city_c)
        else:
            self.filter_reg_comboBox.addItems([''] + comdict['reg_list'])
            self.filter_region_comboBox.addItems([''] + comdict['region_list'])
            self.filter_city_comboBox.addItems([''] + comdict['city_list'])
            
            self.filter_reg_comboBox.setCurrentText(comdict['reg_main'])
            self.filter_region_comboBox.setCurrentText(comdict['region_main'])
            self.filter_city_comboBox.setCurrentText(comdict['city_main'])
        
        self.filter_takepart_comboBox.setCurrentText(f_takepart_c)
        # Временно отключаем сигнал currentIndexChanged
        self.connect_on_off_filter(True)
    
    
    def update_filter_cB(self, colname: str, widget_: str):
        dict_cB = Edit_Row.get_less_list(self, colname, widget_)
        self.fill_filter_comboBox(dict_cB)
    
    
    def connect_on_off_filter(self, flag: bool = True):
        if flag:
            self.filter_reg_comboBox.currentTextChanged.connect(lambda: self.update_filter_cB('Округ', 'filter_reg_comboBox'))
            self.filter_region_comboBox.currentTextChanged.connect(lambda: self.update_filter_cB('Регион', 'filter_region_comboBox'))
            self.filter_city_comboBox.currentTextChanged.connect(lambda: self.update_filter_cB('Город', 'filter_city_comboBox'))
        else:
            self.filter_reg_comboBox.currentTextChanged.disconnect()
            self.filter_region_comboBox.currentTextChanged.disconnect()
            self.filter_city_comboBox.currentTextChanged.disconnect()
    
    def apply_filter_widget(self) -> None:
        filters = (
            self.filter_region_comboBox.currentText(),
            self.filter_reg_comboBox.currentText(),
            self.filter_city_comboBox.currentText(),
            self.filter_grnti_lineEdit.text(),
            self.filter_grnti2_lineEdit.text(),
            self.filter_keywords_lineEdit.text(),
            self.filter_takepart_comboBox.currentText()
        )
        cols = 'Регион', 'Округ', 'Город', 'ГРНТИ1', 'ГРНТИ2', 'Ключевые слова', 'Участие'
        filter_string: str = self.get_filter_str(filters, cols)
        if filter_string: self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df'].query(filter_string)))
        else:             self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        self.filter_widget.setHidden(True)
        
        self.filterlist_name.setText(f'  Фильтр:  {";  ".join(filter_ for filter_ in filters if filter_)}')
        self.filterlist_name.setHidden(False)
        
        self.namberlines_name.setText(f'  Число строк:  {self.init_table.model().init_data.shape[0]}')
        
        
    def get_filter_str(self, filters: tuple[str, ...], cols: tuple[str, ...]) -> str:
        flag = len(list(f for f, c in zip(filters, cols) if c in ['ГРНТИ1', 'ГРНТИ2'] and f != '')) == 2
        filter_string: str = ''
        for filter_, col_ in zip(filters, cols):
            if filter_ == '': continue
            match col_:
                case 'Ключевые слова':
                    if len(filter_string) > 1: filter_string += ' and '
                    filter_ = filter_.split(',')
                    for n, i in enumerate(filter_):
                        filter_string += f'`{col_.strip()}`.str.contains(r"{i}", na=False, case=False, regex=True)'
                        if len(filter_) - (n + 1): filter_string += ' or '
                case 'ГРНТИ1':
                    if len(filter_string) > 1: filter_string += ' and '
                    if flag: filter_string += '('
                    filter_string += f'`ГРНТИ`.str.contains(r"(?:^{filter_}|, {filter_})", regex=True)'
                case 'ГРНТИ2':
                    if flag:
                        filter_string += ' or '
                    elif len(filter_string) > 1: filter_string += ' and '
                    filter_string += f'`ГРНТИ`.str.contains(r"(?:^{filter_}|, {filter_})", regex=True)'
                    if flag: 
                        filter_string += ')'
                        flag = False
                case 'Участие':
                    if len(filter_string) > 1: filter_string += ' and '
                    filter_string += f'`{col_}` == {filter_}'
                case _:
                    if len(filter_string) > 1: filter_string += ' and '
                    filter_string += f'`{col_}`.str.contains("{filter_}", na=False, case=False)'
        # print(f'{filter_string = }')
        return filter_string
    
    
    def show_filter_widget(self, hide: bool) -> None: 
        self.fill_filter_comboBox()
        if not hide:
            if self.filter_city_comboBox.currentText()      : self.update_filter_cB('Город', 'filter_city_comboBox')
            elif self.filter_region_comboBox.currentText()  : self.update_filter_cB('Регион', 'filter_region_comboBox')
            elif self.filter_reg_comboBox.currentText()     : self.update_filter_cB('Округ', 'filter_reg_comboBox')
        self.filter_widget.setHidden(hide)  
        
        
    def reset_filter_widget(self) -> None:
        self.filter_region_comboBox.setCurrentText('')
        self.filter_reg_comboBox.setCurrentText('')
        self.filter_city_comboBox.setCurrentText('')
        self.filter_grnti_lineEdit.setText('')
        self.filter_grnti2_lineEdit.setText('')
        self.filter_keywords_lineEdit.setText('')
        self.filter_takepart_comboBox.setCurrentText('')
        
        self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        self.namberlines_name.setText(f'  Число строк:  {self.df_ntp.shape[0]}')
        self.filterlist_name.setHidden(True)