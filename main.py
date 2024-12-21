import os, subprocess, sys
for name in ('exit', 'Dialog_confirm', 'Dialog_comboBox', 'Dialog_lineEdit'):
    if not os.path.isfile(f'{name}.py'):
        match sys.platform:
            case 'darwin': subprocess.run(f'pyuic6 -o {name}.py -x {name}.ui'.split())
            case _: subprocess.run(f'python -m PyQt6.uic.pyuic -o {name}.py -x {name}.ui'.split())    

from utils._add import Add_Row
from utils._edit import Edit_Row
from utils._base import Base_Class, Ui_Dialog_confirm, Ui_Dialog_lineEdit, Ui_Dialog_comboBox, Ui_plug
from utils._table import Table_Methods
from utils._filter import Filter_table
from utils._delete import Delete_rows
from utils._experts import Experts

from PyQt6.QtWidgets import QApplication

import pandas as pd

pd.set_option('future.no_silent_downcasting', True)


class Ui_MainWindow2(Edit_Row, Add_Row, Table_Methods, Filter_table, Delete_rows, Experts):

    def __init__(self):
        # Загружаем данные и всякие переменные
        Base_Class.__init__(self)
        
        # Отобразить пустую страницу
        self.start_position()
        # Подключаем сигнал нажатия кнопки к методу
        self.btn_connect()
        # Привязка клавиш
        self.keyboard_connect()
        # Работа со слоями
        self.layers()
        
        # Скрыть предупреждение
        Delete_rows.__init__(self)
        # Заполнить поля в Добавить
        Add_Row.__init__(self)
        # Заполнить поля в Фильтр
        Filter_table.__init__(self)
        # Заполнить поля в Редактировать
        Edit_Row.__init__(self)
        # Подготовка к Сотрировке
        Table_Methods.__init__(self)
        # Подготовка к Сотрировке
        Experts.__init__(self)
        
        # Отображение "Эксперты НТП"
        self.show_table('ntp')
   
    def open_dialog(self, string):
        func_before = {
            'add'   : self.before_add_widget,
            'edit'  : self.before_edit_widget,
            'delete': self.before_delete_widget,
            'new_group' : self.before_group_widget,
            'choose_group' : lambda: True,
            'merge_group' : lambda: True,
            'delete_group' : self.before_delete_expert_widget,
            'delete_group_part' : self.before_delete_expert_part_widget
        }
        dialog_ui = {
            'add'   : Ui_plug,
            'edit'  : Ui_plug,
            'delete': Ui_Dialog_confirm,
            'new_group' : Ui_Dialog_lineEdit,
            'save_group' : Ui_Dialog_lineEdit,
            'merge_group' : Ui_Dialog_comboBox,
            'choose_group' : Ui_Dialog_comboBox,
            'delete_group' : Ui_Dialog_confirm,
            'delete_group_part' : Ui_Dialog_confirm
        }
        func_after = {
            'add'   : self.apply_add_widget,
            'edit'  : self.apply_edit_widget,
            'delete': self.apply_delete_widget,
            'new_group' : self.save_group_widget,
            'save_group' : self.save_group_widget,
            'merge_group' : self.merge_group_widget,
            'choose_group' : self.groups_show,
            'delete_group' : self.apply_delete_expert_widget,
            'delete_group_part' : self.apply_delete_expert_part_widget 
        }
        if not func_before[string]():
            return
        if string == 'new_group': string = self.save_or_new_group()
        dialog = dialog_ui[string](string)
        result = dialog.exec()  # Запускаем диалоговое окно и ожидаем результата
        match result:
            case 1: func_after[string]()
            case 0: return 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_MainWindow2()
    ui.show()
    sys.exit(app.exec())