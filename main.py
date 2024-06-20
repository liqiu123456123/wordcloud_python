import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QColorDialog, \
    QComboBox, QScrollArea, QLabel
from PyQt5.QtCore import Qt  # 导入 QtCore.Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from wordcloud import WordCloud
import jieba
import numpy as np
from PIL import Image
from PyQt5.QtGui import QFont, QPixmap
import os


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.color_code = None
        self.mask_shape = None
        self.ch_font = None
        self.stop_words = None
        self.texts = []
        self.initUI()

    def initUI(self):
        self.font_dict = {'楷体': 'simkai.ttf', '隶书': 'SIMLI.TTF', '宋体': 'simsun.ttc', '黑体': 'simhei.ttf',
                          '微软雅黑': 'msyh.ttc'}
        # 创建布局
        vbox = QVBoxLayout()
        # 第一部分：横向排列的按钮和组合框
        button_list = ["选择文本", "选择停用词", "选择背景颜色", "导出词云图", "选择词云图形状", "选择字体"]
        self.font_type = QComboBox(self)
        for key in self.font_dict:
            self.font_type.addItem(key)
        hbox1 = QHBoxLayout()
        for i in range(6):
            btn = QPushButton(button_list[i])
            self.font = QFont('微软雅黑', 12, QFont.Bold)
            btn.setFont(self.font)
            btn.setStyleSheet("QPushButton { color: #E0E0E0; background-color: #333333; }")
            if button_list[i] == "选择文本":
                btn.clicked.connect(self.openTextFiles)
            elif button_list[i] == "选择停用词":
                btn.clicked.connect(self.openStopWordsFile)
            elif button_list[i] == "选择背景颜色":
                btn.setObjectName("选择背景颜色")
                btn.clicked.connect(self.selectBackgroundColor)
            elif button_list[i] == "选择词云图形状":
                btn.setObjectName("选择词云图形状")
                btn.clicked.connect(self.open_mask_img)
            else:
                btn.clicked.connect(self.save_wordcloud_image)
            hbox1.addWidget(btn)
        self.font_type.setStyleSheet(
            "QComboBox { color: #E0E0E0; background-color: #333333; } QComboBox QAbstractItemView { background-color: #333333; } ")
        self.font_type.setFont(self.font)
        hbox1.addWidget(self.font_type)
        vbox.addLayout(hbox1)

        # 第二部分：一个按钮
        btn_single = QPushButton('更新词云图')
        btn_single.setFont(self.font)
        btn_single.setStyleSheet("QPushButton { color: #E0E0E0; background-color: #333333; }")
        btn_single.clicked.connect(self.update_wordclouds)  # 连接点击事件
        vbox.addWidget(btn_single)

        # 第三部分：滚动区域，用于显示多个词云图
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout()
        self.scroll_area_widget.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)
        vbox.addWidget(self.scroll_area)

        # 设置窗口属性
        self.setLayout(vbox)
        self.setWindowTitle('基于Python开发的批量词云图生成系统')
        self.setGeometry(500, 100, 1200, 840)
        self.setStyleSheet("background-color: #2E4053;")
        self.show()

    def open_mask_img(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "选择词云图形状", "",
                                                  "Image Files (*.png *.xpm *.jpg *.jpeg)")
        if fileName:
            self.mask_shape = np.array(Image.open(fileName))

    def save_wordcloud_image(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "保存词云图", "",
                                                  "PNG Files (*.png);;JPG Files (*.jpg);;All Files (*)")
        if fileName:
            # 保存每一个生成的词云图
            for i in range(self.scroll_area_layout.count()):
                label = self.scroll_area_layout.itemAt(i).widget()
                pixmap = label.pixmap()
                pixmap.save(f"{fileName}_{i}.png")
            print(f"词云图已保存为 {fileName}_*.png")

    def update_wordclouds(self):
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        selected_text = self.font_type.currentText()
        self.ch_font = self.font_dict[selected_text]

        for text in self.texts:
            word_list = jieba.cut(text, cut_all=False)
            words = " ".join(word_list)
            wordcloud = WordCloud(width=800, height=800,
                                  background_color=self.color_code if self.color_code is not None else "#FFFFFF",
                                  stopwords=self.stop_words if self.stop_words is not None else None,
                                  font_path=self.ch_font if self.ch_font is not None else 'msyh.ttc',
                                  mask=self.mask_shape if self.mask_shape is not None else None).generate(words)

            fig = Figure(figsize=(8, 8), dpi=100)
            axes = fig.add_subplot(111)
            axes.axis("off")
            axes.imshow(wordcloud, interpolation='bilinear')

            canvas = FigureCanvas(fig)
            canvas.draw()

            image_path = f"temp_wc_{len(self.scroll_area_layout)}.png"
            fig.savefig(image_path, dpi=100, bbox_inches='tight')
            pixmap = QPixmap(image_path)

            label = QLabel()
            label.setPixmap(pixmap)

            # 添加居中的布局
            layout = QVBoxLayout()
            layout.addWidget(label)
            layout.setAlignment(label, Qt.AlignCenter)

            widget = QWidget()
            widget.setLayout(layout)

            self.scroll_area_layout.addWidget(widget)
            os.remove(image_path)

    def openTextFiles(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择文本文件", "", "Text Files (*.txt)")
        if files:  # 确保文件路径不为空
            self.texts = []
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as file:  # 读取文本文件内容
                    self.texts.append(file.read())
        else:
            print("未选择文件")

    def openStopWordsFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择停用词文件", "", "Text Files (*.txt)")
        with open(file_path, 'r', encoding='utf-8') as f:
            self.stop_words = set(f.read().splitlines())

    def selectBackgroundColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_code = color.name()
            button = self.findChild(QPushButton, "选择背景颜色")
            button.setText(self.color_code)
            button.setStyleSheet(f"color: {self.color_code};")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
