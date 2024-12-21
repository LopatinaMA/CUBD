from utils._base import Base_Class, pandasModel

from PyQt6.QtCore import QModelIndex

class Table_Methods(Base_Class):
    
    def __init__(self):
        self.init_table.setSortingEnabled(True)
        self.flag_sort: bool = True
        self.col_sort: int = 0
        self.init_table.horizontalHeader().sectionClicked.connect(self.sort_table)
    
    def show_table(self, name: str) -> None:
        self.cur_name = name
        match name:
            case 'reg' | 'grnti' : self.start_position(btns=True)
            case 'ntp'           : self.start_position(btns=False)
        df_ = self.settings_dict[name]
        self.init_table.setModel(pandasModel(df_['df']))
        self.init_table.setSelectionMode(df_['mode'])
        self.init_table.setSelectionBehavior(df_['behave'])
        self.init_tablename.setText(df_['label'])
        self.namberlines_name.setText(f'  Число строк:  {df_["df"].shape[0]}')
        self.init_table.resizeColumnsToContents()
        # Укорачивание столбца Расшифровка
        for id, col in enumerate(self.init_table.model().init_data.columns):
            if col == 'Расшифровка':
                self.init_table.setColumnWidth(id, 487); break
        self.stackedWidget.setCurrentWidget(self.page_1)
    
    def sort_table(self, col: int) -> None:
        match self.col_sort == col:
            case True  : self.flag_sort = not self.flag_sort
            case False : self.flag_sort = True

        self.col_sort = col
        a = self.init_table.model().init_data
        a = a.sort_values(by=a.columns[col], axis=0, ascending=self.flag_sort)
        self.init_table.setModel(pandasModel(a))
    
    def select_all_rows(self, flag: bool):
        if flag:
            self.init_table.selectAll()
        else:
            self.init_table.setCurrentIndex(QModelIndex())