# -*- coding: utf-8 -*-
"""
生成《社会调查实践》作业一完整提交文档（Word + PDF）并打包 ZIP
学生：汤晋欢  学号：24307090021
所有统计数字 100% 严格对应 汤晋欢+24307090021_运行日志.log
"""

import os
import shutil
import zipfile
import docx
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

def set_run_font(run, font_cn="宋体", font_en="Times New Roman", size=10.5, bold=False, italic=False, color=None):
    run.font.name = font_en
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_cn)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def apply_three_line_table(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        bdr = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
            f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(bdr)
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F2F4F8"/>')
        tcPr.append(shd)
    for cell in table.rows[-1].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        bdr = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(bdr)

def fill_table(doc, headers, rows, col_widths, alignments):
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for c_idx, h in enumerate(headers):
        cell = table.rows[0].cells[c_idx]
        cell.width = Cm(col_widths[c_idx])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        set_run_font(r, font_cn="黑体", size=9.0, bold=True)
    for r_idx, row_data in enumerate(rows, start=1):
        row = table.rows[r_idx]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = Cm(col_widths[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=55, bottom=55, left=80, right=80)
            p = cell.paragraphs[0]
            p.alignment = alignments[c_idx]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(str(val))
            set_run_font(r, font_cn="宋体", size=8.5, bold=(c_idx == 0 and str(val).strip() != ""))
    apply_three_line_table(table)
    return table

# 1. 变量对照表数据（严格对应 汤晋欢+24307090021_运行日志.log）
VAR_MAP_HEADERS = ["变量名", "CGSS 2023 题号", "变量含义", "测量层次", "构造方式（含缺失值处理）", "有效样本量"]
VAR_MAP_ROWS = [
    ("comp_jhs", "a7a", "阶段一：完成初中（是否升入初中）", "名义（二分类）",
     "a7a（最高教育程度）负值(-5/-1)及14(其他)设为系统缺失(.)；小学及以下(1–3)=0，初中及以上(4–13)=1。风险集为全体有效入户样本。", "5,582"),
    ("comp_shs", "a7a", "阶段二：完成高中（初中毕业是否升学）", "名义（二分类）",
     "限定在完成初中（comp_jhs=1）的风险子样本中：初中毕业即止(a7a=4)=0，普通高中/职高/中专/技校及以上(a7a=5–13)=1；未完成初中者设为系统缺失(.)。", "3,641"),
    ("comp_univ", "a7a", "阶段三：完成大学（高中毕业是否升学）", "名义（二分类）",
     "限定在完成高中阶段（comp_shs=1）的风险子样本中：高中/中职毕业即止(a7a=5–8)=0，大专/本科/研究生及以上(a7a=9–13)=1；未完成高中者设为系统缺失(.)。", "2,023"),
    ("edu_yrs", "a7a", "被访者受教育年限（年）", "连续",
     "按现行学制折算：无教育(1)=0，私塾/扫盲班(2)=1，小学(3)=6，初中(4)=9，高中/职高/中专/技校(5–8)=12，大专(9–10)=15，本科(11–12)=16，研究生及以上(13)=19；-5/-1及14设缺失。", "5,582"),
    ("edu_level", "a7a", "被访者最高教育层次", "有序",
     "按 a7a 归并为四层级：1=小学及以下(1–3)，2=初中(4)，3=高中/中职(5–8)，4=大学及以上(9–13)；-5/-1及14设缺失。", "5,582"),
    ("f_isei", "isco08f", "被访者14岁时父亲职业地位 ISEI", "连续",
     "先将 isco08f 负值(-5/-1，共827例)设为缺失；调用 Stata 的 iscogen 依据 Ganzeboom (2010) 标准转换表将四位 ISCO-08 职业编码映射为 ISEI-08 连续得分(10–89)。", "4,756"),
    ("f_isei10", "isco08f", "父亲职业地位（ISEI/10，入模变量）", "连续",
     "由 f_isei 除以 10 生成（取值范围 1.0–8.9），使回归优势比对应父亲 ISEI 每提升 10 个单位的边际效应，与复刻原文保持一致。", "4,756"),
    ("f_edu", "a89b", "父亲受教育年限（年）", "连续",
     "a89b 负值(-5/-1，共302例)及14设为缺失；按与被访者相同的中国学制折算表映射为连续受教育年限（0–19年）。", "5,238"),
    ("m_edu", "a90b", "母亲受教育年限（年）", "连续",
     "a90b 负值(-5/-1，共158例)及14设为缺失；按相同学制折算规则映射为连续受教育年限（0–16年）。", "5,411"),
    ("pedu_max", "a89b, a90b", "父母最高受教育年限（年）", "连续",
     "采用家庭文化资本最大化原则，通过 egen rowmax(f_edu m_edu) 取父母受教育年限较高一方；若仅一方有效则取有效方，双方均缺失(104例)则设为缺失。", "5,479"),
    ("female", "a2", "性别（女=1）", "名义（二分类）",
     "a2 负值(-5/-1)设缺失；将 a2=1(男)编码为 0，a2=2(女)编码为 1。", "5,583"),
    ("minority", "a4", "民族身份（少数民族=1）", "名义（二分类）",
     "a4 负值(-5/-1)设缺失；a4=1(汉族)编码为 0，a4=2–8(蒙、满、回、藏、壮、维及其他少数民族)编码为 1。", "5,583"),
    ("age", "a3a", "被访者周岁年龄", "连续",
     "a3a（出生年份）负值(-5/-1)设缺失；由调查年份减去出生年份计算：age = 2023 - a3a（取值 18–94 岁）。", "5,583"),
    ("cohort", "a3a", "出生历史队列", "有序",
     "按出生年份划分为5个历史阶段：1=1960及以前，2=1961–1970，3=1971–1980，4=1981–1990，5=1991及以后。", "5,583"),
    ("rural_hukou", "a18", "户口登记性质（农业户口=1）", "名义（二分类）",
     "a18 负值(-5/-1)及6–7(无户口/其他，共7例)设缺失；a18=1(农业户口)编码为 1，a18=2–5(非农业户口/居民户口/军籍)编码为 0。", "5,576"),
    ("f_class14", "a43d", "14岁时家庭主观社会阶层", "有序（视为连续）",
     "a43d 负值(-5/-1，共87例)设缺失；保留 1（最底层）至 10（最顶层）的十分制梯子量表得分，作为早年家庭先赋社会位置的补充控制。", "5,496"),
    ("f_party", "a89c", "父亲政治面貌（中共党员=1）", "名义（二分类）",
     "a89c 负值(-5/-1，共111例)设缺失；a89c=4(共产党员)编码为 1，a89c=1–3(群众/共青团员/民主党派)编码为 0。", "5,472"),
    ("income", "a8a", "个人去年全年总收入（元）", "连续",
     "a8a 负值(-5/-1)及特殊缺失码 9999997–9999999(不知道/拒绝回答，共224例)设为缺失；顶码 9999996 赋值为 1,000,000；保留 0 收入。", "5,359"),
    ("lninc", "a8a", "个人年收入对数 ln(x+1)", "连续",
     "对清理后的 income 取自然对数变换 ln(income + 1)，既避免零收入样本在取对数时脱落，又缓解原始收入的严重右偏分布。", "5,359"),
    ("lninc_win", "a8a", "个人年收入对数（1%/99%缩尾）", "连续",
     "在 lninc 基础上按第 1 百分位(0.00)与第 99 百分位(12.74)进行双侧缩尾（Winsorization，替换上尾极端值53例），消除极端异常值干扰。", "5,359"),
    ("weight", "weight1", "个人层级抽样权重", "连续（权重）",
     "直接提取 CGSS 2023 官方个人层级代表性权重变量 weight1，用于描述统计的加权均值与加权频数占比估计。", "5,583"),
]

# 2. 连续变量描述统计表（严格对应日志第7、8步）
CONT_HEADERS = ["变量名", "变量含义", "有效N", "未加权均值", "未加权标准差", "加权均值", "加权标准差", "最小值", "最大值"]
CONT_ROWS = [
    ("edu_yrs", "被访者受教育年限（年）", "5,582", "9.02", "4.58", "9.68", "4.55", "0", "19"),
    ("f_isei", "父亲14岁时职业地位（ISEI-08）", "4,756", "22.02", "18.65", "20.90", "17.92", "10", "89"),
    ("f_isei10", "父亲职业地位（ISEI/10）", "4,756", "2.20", "1.86", "2.09", "1.79", "1.00", "8.90"),
    ("f_edu", "父亲受教育年限（年）", "5,238", "4.60", "4.58", "5.13", "4.58", "0", "19"),
    ("m_edu", "母亲受教育年限（年）", "5,411", "2.98", "4.13", "3.50", "4.28", "0", "16"),
    ("pedu_max", "父母最高受教育年限（年）", "5,479", "4.74", "4.68", "5.34", "4.68", "0", "19"),
    ("age", "被访者年龄（岁）", "5,583", "54.60", "16.34", "48.70", "16.84", "18", "94"),
    ("f_class14", "14岁时家庭主观阶层（1–10分）", "5,496", "3.31", "2.04", "3.31", "1.94", "1", "10"),
    ("income", "个人去年总收入（元）", "5,359", "43,936.97", "247,673.10", "45,332.27", "242,330.40", "0", "9,991,300"),
    ("lninc", "个人年收入对数 ln(x+1)", "5,359", "8.29", "3.97", "8.28", "4.04", "0.00", "16.12"),
    ("lninc_win", "个人年收入对数（1%/99%缩尾）", "5,359", "8.28", "3.96", "8.28", "4.03", "0.00", "12.74"),
]

# 3. 分类变量描述统计表（严格对应日志第9、10步）
CAT_HEADERS = ["变量名", "变量含义", "类别编码与名称", "未加权频数", "未加权有效占比(%)", "加权频数", "加权有效占比(%)"]
CAT_ROWS = [
    ("comp_jhs", "阶段一：完成初中（N=5,582）", "0 = 小学及以下（未完成初中）", "1,941", "34.77", "1,602.41", "28.70"),
    ("", "", "1 = 初中及以上（升入初中）", "3,641", "65.23", "3,980.27", "71.30"),
    ("comp_shs", "阶段二：完成高中（N=3,641）", "0 = 初中毕业即止（未升高中）", "1,618", "44.44", "1,679.80", "42.20"),
    ("", "", "1 = 高中/中职及以上（升入高中）", "2,023", "55.56", "2,300.47", "57.80"),
    ("comp_univ", "阶段三：完成大学（N=2,023）", "0 = 高中毕业即止（未升大学）", "1,037", "51.26", "1,042.87", "45.33"),
    ("", "", "1 = 大学专科/本科及以上（升入大学）", "986", "48.74", "1,257.60", "54.67"),
    ("edu_level", "最高受教育程度层次（N=5,582）", "1 = 小学及以下", "1,941", "34.77", "1,602.41", "28.70"),
    ("", "", "2 = 初中", "1,618", "28.99", "1,679.80", "30.09"),
    ("", "", "3 = 高中/中职", "1,037", "18.58", "1,042.87", "18.68"),
    ("", "", "4 = 大学及以上", "986", "17.66", "1,257.60", "22.53"),
    ("female", "性别（N=5,583）", "0 = 男", "2,503", "44.83", "2,791.29", "50.00"),
    ("", "", "1 = 女", "3,080", "55.17", "2,791.71", "50.00"),
    ("minority", "民族身份（N=5,583）", "0 = 汉族", "5,064", "90.70", "5,012.75", "89.79"),
    ("", "", "1 = 少数民族", "519", "9.30", "570.25", "10.21"),
    ("cohort", "出生历史队列（N=5,583）", "1 = 1960及以前", "1,978", "35.43", "1,283.01", "22.98"),
    ("", "", "2 = 1961–1970", "1,282", "22.96", "1,106.27", "19.81"),
    ("", "", "3 = 1971–1980", "964", "17.27", "1,060.74", "19.00"),
    ("", "", "4 = 1981–1990", "717", "12.84", "1,036.34", "18.56"),
    ("", "", "5 = 1991及以后", "642", "11.50", "1,096.64", "19.64"),
    ("rural_hukou", "户口登记性质（N=5,576）", "0 = 非农业/居民户口", "2,200", "39.45", "1,898.13", "34.04"),
    ("", "", "1 = 农业户口", "3,376", "60.55", "3,678.46", "65.96"),
    ("f_party", "父亲政治面貌（N=5,472）", "0 = 非中共党员", "4,761", "87.01", "4,861.75", "88.28"),
    ("", "", "1 = 中共党员", "711", "12.99", "645.62", "11.72"),
]
