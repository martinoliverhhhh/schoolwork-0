# -*- coding: utf-8 -*-
"""
生成作业一专业描述统计表 Excel 文件
汤晋欢 24307090021
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# Sheet 1: 连续变量描述统计
ws1 = wb.active
ws1.title = "连续变量描述统计"

# Header Title
ws1.merge_cells("A1:I1")
title_cell = ws1["A1"]
title_cell.value = "表1  主要分析连续变量描述统计表（CGSS 2023入户面访样本）"
title_cell.font = Font(name="黑体", size=14, bold=True, color="1F497D")
title_cell.alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[1].height = 30

ws1.merge_cells("A2:I2")
sub_cell = ws1["A2"]
sub_cell.value = "注：样本限定为CGSS 2023入户面访有效成人样本（N=5,583）。加权统计使用个人层级抽样权重（weight1）。"
sub_cell.font = Font(name="宋体", size=10, italic=True, color="595959")
sub_cell.alignment = Alignment(horizontal="left", vertical="center")
ws1.row_dimensions[2].height = 20

# Column headers
headers_cont = [
    "变量名", "变量标签/含义", "有效样本量(N)", "未加权均值", "未加权标准差", 
    "加权均值", "加权标准差", "最小值", "最大值"
]

header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
header_font = Font(name="宋体", size=11, bold=True, color="FFFFFF")
thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='1F497D'),
    bottom=Side(style='medium', color='1F497D')
)
data_border = Border(
    left=Side(style='thin', color='E0E0E0'),
    right=Side(style='thin', color='E0E0E0'),
    top=Side(style='thin', color='E0E0E0'),
    bottom=Side(style='thin', color='E0E0E0')
)

ws1.row_dimensions[3].height = 26
for col_num, h in enumerate(headers_cont, 1):
    cell = ws1.cell(row=3, column=col_num)
    cell.value = h
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = thin_border

cont_data = [
    ("edu_yrs", "被访者受教育年限（年）", 5582, 9.02, 4.58, 9.68, 4.55, 0, 19),
    ("f_isei", "父亲14岁时职业地位（ISEI-08）", 4756, 22.02, 18.65, 20.90, 17.92, 10, 89),
    ("f_isei10", "父亲职业地位（ISEI/10，进入模型）", 4756, 2.20, 1.86, 2.09, 1.79, 1.0, 8.9),
    ("f_edu", "父亲受教育年限（年）", 5238, 4.60, 4.58, 5.13, 4.58, 0, 19),
    ("m_edu", "母亲受教育年限（年）", 5411, 2.98, 4.13, 3.50, 4.28, 0, 16),
    ("pedu_max", "父母最高受教育年限（年）", 5479, 4.74, 4.68, 5.34, 4.68, 0, 19),
    ("age", "被访者年龄（岁）", 5583, 54.60, 16.34, 48.70, 16.84, 18, 94),
    ("f_class14", "14岁时家庭主观阶层（1-10分）", 5496, 3.31, 2.04, 3.31, 1.94, 1, 10),
    ("income", "个人去年总收入（元）", 5359, 43936.97, 247673.10, 45332.27, 242330.40, 0, 9991300),
    ("lninc", "个人年收入对数 ln(x+1)", 5359, 8.29, 3.97, 8.28, 4.04, 0.00, 16.12),
    ("lninc_win", "个人年收入对数（1%/99%双侧缩尾）", 5359, 8.28, 3.96, 8.28, 4.03, 0.00, 12.74),
]

alt_fill = PatternFill(start_color="F2F5F9", end_color="F2F5F9", fill_type="solid")

for r_idx, row in enumerate(cont_data, 4):
    ws1.row_dimensions[r_idx].height = 22
    for c_idx, val in enumerate(row, 1):
        cell = ws1.cell(row=r_idx, column=c_idx)
        cell.value = val
        cell.font = Font(name="宋体", size=10)
        cell.border = data_border
        if r_idx % 2 == 1:
            cell.fill = alt_fill
        
        if c_idx in [1, 2]:
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_idx == 3:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.number_format = "#,##0"
        elif c_idx in [4, 5, 6, 7]:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0.00"
        else:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            if isinstance(val, float):
                cell.number_format = "#,##0.00"
            else:
                cell.number_format = "#,##0"

# Sheet 2: 分类变量描述统计
ws2 = wb.create_sheet(title="分类变量描述统计")

ws2.merge_cells("A1:H1")
title2 = ws2["A1"]
title2.value = "表2  主要分析分类变量频数与占比分布表（CGSS 2023入户面访样本）"
title2.font = Font(name="黑体", size=14, bold=True, color="1F497D")
title2.alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[1].height = 30

ws2.merge_cells("A2:H2")
sub2 = ws2["A2"]
sub2.value = "注：加权占比基于个人抽样权重（weight1）计算。升学转换变量为各阶段所对应的风险人群子样本。"
sub2.font = Font(name="宋体", size=10, italic=True, color="595959")
sub2.alignment = Alignment(horizontal="left", vertical="center")
ws2.row_dimensions[2].height = 20

headers_cat = [
    "变量名", "变量标签/含义", "类别编码", "类别名称", 
    "未加权频数(N)", "未加权占比(%)", "加权频数", "加权占比(%)"
]

ws2.row_dimensions[3].height = 26
for col_num, h in enumerate(headers_cat, 1):
    cell = ws2.cell(row=3, column=col_num)
    cell.value = h
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = thin_border

cat_data = [
    ("comp_jhs", "阶段一：完成初中（全样本风险）", 0, "小学及以下（未完成初中）", 1941, 34.77, 1602.41, 28.70),
    ("", "", 1, "初中及以上（成功升入初中）", 3641, 65.23, 3980.27, 71.30),
    ("comp_shs", "阶段二：完成高中（初中毕业生子样本）", 0, "初中毕业即止（未升入高中）", 1618, 44.44, 1679.80, 42.20),
    ("", "", 1, "高中/中职及以上（成功升学）", 2023, 55.56, 2300.47, 57.80),
    ("comp_univ", "阶段三：完成大学（高中毕业生子样本）", 0, "高中阶段毕业即止（未升入大学）", 1037, 51.26, 1042.87, 45.33),
    ("", "", 1, "大学专科/本科及以上（成功升学）", 986, 48.74, 1257.60, 54.67),
    ("edu_level", "最高受教育程度层次", 1, "小学及以下", 1941, 34.77, 1602.41, 28.70),
    ("", "", 2, "初中", 1618, 28.99, 1679.80, 30.09),
    ("", "", 3, "高中/中专/技校/职高", 1037, 18.58, 1042.87, 18.68),
    ("", "", 4, "大学专科/大学本科及以上", 986, 17.66, 1257.60, 22.53),
    ("female", "性别", 0, "男", 2503, 44.83, 2791.29, 50.00),
    ("", "", 1, "女", 3080, 55.17, 2791.71, 50.00),
    ("minority", "民族身份", 0, "汉族", 5064, 90.70, 5012.75, 89.79),
    ("", "", 1, "少数民族", 519, 9.30, 570.25, 10.21),
    ("cohort", "出生历史队列", 1, "1960及以前（前改革时代）", 1978, 35.43, 1283.01, 22.98),
    ("", "", 2, "1961-1970（恢复高考初期）", 1282, 22.96, 1106.27, 19.81),
    ("", "", 3, "1971-1980（改革推进期）", 964, 17.27, 1060.74, 19.00),
    ("", "", 4, "1981-1990（九年义务教育普及期）", 717, 12.84, 1036.34, 18.56),
    ("", "", 5, "1991及以后（高等教育大众化期）", 642, 11.50, 1096.64, 19.64),
    ("rural_hukou", "户口登记性质", 0, "非农业户口/居民户口/军籍", 2200, 39.45, 1898.13, 34.04),
    ("", "", 1, "农业户口", 3376, 60.55, 3678.46, 65.96),
    ("f_party", "父亲政治面貌", 0, "非中共党员（群众/团员/民主党派）", 4761, 87.01, 4861.75, 88.28),
    ("", "", 1, "中共党员", 711, 12.99, 645.62, 11.72),
]

for r_idx, row in enumerate(cat_data, 4):
    ws2.row_dimensions[r_idx].height = 21
    for c_idx, val in enumerate(row, 1):
        cell = ws2.cell(row=r_idx, column=c_idx)
        cell.value = val
        cell.font = Font(name="宋体", size=10)
        cell.border = data_border
        
        # Zebra shading by group
        if r_idx in [4, 5, 8, 9, 10, 11, 14, 15, 21, 22, 25, 26]:
            cell.fill = alt_fill
            
        if c_idx in [1, 2, 4]:
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_idx == 3:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif c_idx == 5:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
        elif c_idx == 6:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "0.00"
        elif c_idx == 7:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0.00"
        elif c_idx == 8:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "0.00"

# Auto-adjust column widths
for ws in [ws1, ws2]:
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            # ignore merged title rows
            if cell.row in [1, 2]:
                continue
            v = str(cell.value or "")
            # calculate width accommodating Chinese chars
            w = sum(2 if ord(c) > 127 else 1 for c in v)
            if w > max_len:
                max_len = w
        ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

excel_path = "汤晋欢+24307090021_描述统计表.xlsx"
wb.save(excel_path)
print(f"Excel workbook saved: {excel_path}")
