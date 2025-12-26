"""
UI Styles for PyQt5 Application
"""


class Styles:
    """
    Central styles definition for the application
    """
    
    @staticmethod
    def get_stylesheet():
        """
        Get the complete stylesheet for the application
        
        Returns:
            str: Complete CSS stylesheet
        """
        return """
/* BACKGROUND FRAME */
#bg_frame {
    background-color: #2c313c;
    border-radius: 10px;
}

/* TITLE BAR */
#title_bar {
    background-color: #1b1e23;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}

#window_title {
    color: #c3ccdf;
    font-size: 12pt;
    font-weight: bold;
    padding-left: 10px;
}

#title_btn {
    background-color: transparent;
    border: none;
    color: #c3ccdf;
    font-size: 11pt;
    font-weight: bold;
    border-radius: 5px;
}

#title_btn:hover {
    background-color: #3c4454;
}

#close_btn {
    background-color: transparent;
    border: none;
    color: #c3ccdf;
    font-size: 11pt;
    font-weight: bold;
    border-radius: 5px;
}

#close_btn:hover {
    background-color: #da3838;
}

/* CONTENT FRAME */
#content_frame {
    background-color: #21252d;
    border-radius: 5px;
}

/* TAB WIDGET */
#main_tabs {
    background-color: transparent;
}

#main_tabs::pane {
    border: 2px solid #3c4454;
    border-radius: 5px;
    background-color: #21252d;
    top: -1px;
}

#main_tabs::tab-bar {
    left: 10px;
}

#main_tabs QTabBar::tab {
    background-color: #2c313c;
    color: #8a95aa;
    border: 2px solid #3c4454;
    border-bottom: none;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    padding: 12px 30px;
    margin-right: 5px;
    font-size: 11pt;
    font-weight: bold;
    min-width: 100px;
}

#main_tabs QTabBar::tab:selected {
    background-color: #21252d;
    color: #568af2;
    border-color: #568af2;
}

#main_tabs QTabBar::tab:hover {
    background-color: #3c4454;
    color: #c3ccdf;
}

/* TAB TITLES */
#tab_title {
    color: #c3ccdf;
    font-size: 18pt;
    font-weight: bold;
    padding: 10px;
}

#tab_description {
    color: #8a95aa;
    font-size: 10pt;
    padding: 5px;
}

/* LABELS */
#title_label {
    color: #c3ccdf;
    font-size: 20pt;
    font-weight: bold;
    padding: 10px;
}

#description_label {
    color: #8a95aa;
    font-size: 11pt;
    padding: 5px;
}

#sync_label {
    color: #c3ccdf;
    font-size: 10pt;
    font-weight: bold;
    padding: 5px;
    min-width: 120px;
}

#status_label {
    color: #8a95aa;
    font-size: 9pt;
    padding: 5px;
}

QLabel {
    color: #c3ccdf;
    font-size: 10pt;
    padding: 5px;
}

/* INPUT FIELDS */
#path_input, #settings_input, #search_input {
    background-color: #1b1e23;
    border: 2px solid #3c4454;
    border-radius: 5px;
    color: #c3ccdf;
    padding: 8px;
    font-size: 10pt;
}

#path_input:focus, #settings_input:focus, #search_input:focus {
    border: 2px solid #568af2;
}

/* COMBOBOX */
#settings_combo, #filter_combo {
    background-color: #1b1e23;
    border: 2px solid #3c4454;
    border-radius: 5px;
    color: #c3ccdf;
    padding: 8px;
    font-size: 10pt;
}

#settings_combo:hover, #filter_combo:hover {
    border: 2px solid #568af2;
}

#settings_combo::drop-down, #filter_combo::drop-down {
    border: none;
    padding-right: 10px;
}

#settings_combo::down-arrow, #filter_combo::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #8a95aa;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #1b1e23;
    color: #c3ccdf;
    selection-background-color: #568af2;
    selection-color: #ffffff;
    border: 2px solid #3c4454;
}

/* SPINBOX */
#settings_spinbox {
    background-color: #1b1e23;
    border: 2px solid #3c4454;
    border-radius: 5px;
    color: #c3ccdf;
    padding: 8px;
    font-size: 10pt;
}

#settings_spinbox:focus {
    border: 2px solid #568af2;
}

#settings_spinbox::up-button, #settings_spinbox::down-button {
    background-color: #3c4454;
    border: none;
    border-radius: 3px;
    width: 20px;
}

#settings_spinbox::up-button:hover, #settings_spinbox::down-button:hover {
    background-color: #568af2;
}

/* CHECKBOX */
#settings_checkbox, #sync_checkbox {
    color: #c3ccdf;
    font-size: 10pt;
    spacing: 8px;
}

#settings_checkbox::indicator, #sync_checkbox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #3c4454;
    border-radius: 4px;
    background-color: #1b1e23;
}

#settings_checkbox::indicator:checked, #sync_checkbox::indicator:checked {
    background-color: #568af2;
    border-color: #568af2;
}

#settings_checkbox::indicator:hover, #sync_checkbox::indicator:hover {
    border-color: #568af2;
}

/* GROUPBOX */
#settings_group, #sync_options_group {
    color: #c3ccdf;
    font-size: 10pt;
    font-weight: bold;
    border: 2px solid #3c4454;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}

#settings_group::title, #sync_options_group::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 10px;
    color: #568af2;
}

/* BUTTONS */
#browse_btn {
    background-color: #3c4454;
    border: none;
    border-radius: 5px;
    color: #c3ccdf;
    padding: 8px 15px;
    font-size: 10pt;
    font-weight: bold;
}

#browse_btn:hover {
    background-color: #4a5568;
}

#browse_btn:pressed {
    background-color: #2c313c;
}

#action_btn, #settings_save_btn {
    background-color: #568af2;
    border: none;
    border-radius: 5px;
    color: #ffffff;
    padding: 10px 20px;
    font-size: 10pt;
    font-weight: bold;
}

#action_btn:hover, #settings_save_btn:hover {
    background-color: #6a9bff;
}

#action_btn:pressed, #settings_save_btn:pressed {
    background-color: #4a7ad1;
}

#delete_btn {
    background-color: #da3838;
    border: none;
    border-radius: 5px;
    color: #ffffff;
    padding: 10px 20px;
    font-size: 10pt;
    font-weight: bold;
}

#delete_btn:hover {
    background-color: #e54848;
}

#delete_btn:pressed {
    background-color: #c02828;
}

#sync_btn {
    background-color: #568af2;
    border: none;
    border-radius: 5px;
    color: #ffffff;
    padding: 12px;
    font-size: 12pt;
    font-weight: bold;
}

#sync_btn:hover {
    background-color: #6a9bff;
}

#sync_btn:pressed {
    background-color: #4a7ad1;
}

#sync_btn:disabled {
    background-color: #3c4454;
    color: #6b7280;
}

/* TABLES */
#data_table {
    background-color: #1b1e23;
    alternate-background-color: #21252d;
    color: #c3ccdf;
    gridline-color: #3c4454;
    border: 2px solid #3c4454;
    border-radius: 5px;
    selection-background-color: #568af2;
    selection-color: #ffffff;
}

#data_table QHeaderView::section {
    background-color: #2c313c;
    color: #c3ccdf;
    padding: 8px;
    border: none;
    border-right: 1px solid #3c4454;
    border-bottom: 2px solid #3c4454;
    font-weight: bold;
}

#data_table QHeaderView::section:hover {
    background-color: #3c4454;
}

#data_table::item {
    padding: 5px;
    border: none;
}

#data_table::item:selected {
    background-color: #568af2;
    color: #ffffff;
}

/* PROGRESS BAR */
#progress_bar {
    background-color: #1b1e23;
    border: 2px solid #3c4454;
    border-radius: 5px;
    text-align: center;
    color: #c3ccdf;
}

#progress_bar::chunk {
    background-color: #568af2;
    border-radius: 3px;
}

/* STATUS TEXT */
#status_text {
    background-color: #1b1e23;
    border: 2px solid #3c4454;
    border-radius: 5px;
    color: #c3ccdf;
    font-size: 9pt;
    padding: 10px;
}

/* SCROLL AREA */
#scroll_area {
    background-color: transparent;
    border: none;
}

#scroll_area QWidget {
    background-color: transparent;
}

/* SCROLLBAR */
QScrollBar:vertical {
    background-color: #1b1e23;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #568af2;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6a9bff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background-color: #1b1e23;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #568af2;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #6a9bff;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""

