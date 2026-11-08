# -*- coding: utf-8 -*-
"""
社会调查实践 作业一 数据处理与文档生成脚本
学生：汤晋欢
学号：24307090021
赛道：赛道一——教育、收入与代际地位获得
复刻对象：唐俊超（2015）《输在起跑线——再议中国社会的教育不平等（1978-2008）》
"""

import os
import re
import math
import zipfile
import numpy as np
import pandas as pd
from statsmodels.stats.weightstats import DescrStatsW
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

print("Step 1: Reading CGSS 2023 dataset...")
df = pd.read_pickle('CGSS2023.pkl')
total_raw_n = len(df)
print(f"Raw data total observations: {total_raw_n}")

# Load ISCO-08 mapping from markdown codebook
print("Step 2: Loading ISCO-08 codebook dictionary...")
with open('MinerU_markdown_CGSS2023编码表_2118219675111161856.md', 'r', encoding='utf-8') as f:
    text_cb = f.read()

pattern = re.compile(r'<td><p>(\d{1,4})</p></td>\s*<td><p>(.*?)</p></td>')
label_to_code = {label.strip(): int(code) for code, label in pattern.findall(text_cb)}

# Load Ganzeboom ISEI-08 mapping from iscogen.ado
print("Step 3: Loading Ganzeboom ISCO-08 to ISEI-08 mapping...")
with open('iscogen.ado', 'r', encoding='utf-8') as f:
    text_ado = f.read()

pos = text_ado.find('% CODELIST-isco08-isei')
end_pos = text_ado.find('% END', pos)
codelist = text_ado[pos:end_pos]
isco_to_isei = {}
for line in codelist.splitlines():
    parts = line.strip().split()
    if len(parts) == 2 and parts[0].isdigit():
        isco_to_isei[int(parts[0])] = float(parts[1])

# Filter sample: In-home face-to-face interview sample
print("Step 4: Sample filtering - restricting to in-home interview sample...")
inhome = df[df['isurban'] != '电话调查未调查'].copy()
inhome_n = len(inhome)
print(f"In-home sample size: {inhome_n}")

# Variable Construction
print("Step 5: Constructing variables...")

# 1. Father's ISEI
def get_isei(lbl):
    if pd.isna(lbl) or lbl in ['不适用', '不知道', '拒绝回答', '电话调查未调查']:
        return np.nan
    code = label_to_code.get(lbl, None)
    if code is not None:
        return isco_to_isei.get(code, np.nan)
    return np.nan

inhome['f_isei'] = inhome['isco08f'].apply(get_isei)
inhome['f_isei10'] = inhome['f_isei'] / 10.0

# 2. Education variables
edu_dict = {
    '没有受过任何教育': 0,
    '私塾、扫盲班': 1,
    '小学': 6,
    '初中': 9,
    '职业高中': 12,
    '普通高中': 12,
    '中专': 12,
    '技校': 12,
    '大学专科（成人高等教育）': 15,
    '大学专科（正规高等教育）': 15,
    '大学本科（成人高等教育）': 16,
    '大学本科（正规高等教育）': 16,
    '研究生及以上': 19
}

inhome['edu_yrs'] = inhome['a7a'].map(edu_dict)
inhome['f_edu'] = inhome['a89b'].map(edu_dict)
inhome['m_edu'] = inhome['a90b'].map(edu_dict)
inhome['pedu_max'] = inhome[['f_edu', 'm_edu']].max(axis=1)

# 3. Mare sequential educational transitions
jhs_plus = ['初中', '普通高中', '职业高中', '中专', '技校', '大学专科（成人高等教育）', '大学专科（正规高等教育）', '大学本科（成人高等教育）', '大学本科（正规高等教育）', '研究生及以上']
shs_plus = ['普通高中', '职业高中', '中专', '技校', '大学专科（成人高等教育）', '大学专科（正规高等教育）', '大学本科（成人高等教育）', '大学本科（正规高等教育）', '研究生及以上']
univ_plus = ['大学专科（成人高等教育）', '大学专科（正规高等教育）', '大学本科（成人高等教育）', '大学本科（正规高等教育）', '研究生及以上']

valid_edu_mask = inhome['a7a'].isin(list(edu_dict.keys()))
inhome['comp_jhs'] = np.where(valid_edu_mask, inhome['a7a'].isin(jhs_plus).astype(int), np.nan)
inhome['comp_shs'] = np.where(inhome['comp_jhs'] == 1, inhome['a7a'].isin(shs_plus).astype(int), np.nan)
inhome['comp_univ'] = np.where(inhome['comp_shs'] == 1, inhome['a7a'].isin(univ_plus).astype(int), np.nan)

# 4. Demographic and control variables
inhome['female'] = inhome['a2'].map({'男': 0, '女': 1})
inhome['minority'] = inhome['a4'].apply(lambda x: 0 if x == '汉' else (1 if x in ['蒙', '满', '回', '藏', '壮', '维', '其他'] else np.nan))
inhome['birth_year'] = pd.to_numeric(inhome['a3a'].replace(['不知道', '拒绝回答', '电话调查未调查'], np.nan), errors='coerce')
inhome['age'] = 2023 - inhome['birth_year']

def get_cohort(yr):
    if pd.isna(yr): return np.nan
    if yr <= 1960: return 1
    elif yr <= 1970: return 2
    elif yr <= 1980: return 3
    elif yr <= 1990: return 4
    else: return 5

inhome['cohort'] = inhome['birth_year'].apply(get_cohort)

# Hukou
hukou_map = {'农业户口': 1, '非农业户口': 0, '居民户口（以前是非农业户口）': 0, '居民户口（以前是农业户口）': 0, '军籍': 0}
inhome['rural_hukou'] = inhome['a18'].map(hukou_map)

# Class identity at 14
inhome['f_class14'] = inhome['a43d'].apply(lambda x: int(x.replace('分', '')) if isinstance(x, str) and '分' in x else (int(x) if isinstance(x, (int, float)) and 1 <= x <= 10 else np.nan))

# Father's party affiliation
inhome['f_party'] = inhome['a89c'].map({'共产党员': 1, '群众': 0, '共青团员': 0, '民主党派': 0})

# Personal income
def parse_income(x):
    if pd.isna(x) or str(x) in ['不适用', '不知道', '拒绝回答', '电话调查未调查', '-1', '-2', '-3', '-5', '9999997', '9999998', '9999999']:
        return np.nan
    try:
        val = float(x)
        if val in [-1, -2, -3, -5, 9999997, 9999998, 9999999]: return np.nan
        if val == 9999996: val = 1000000.0
        return val if val >= 0 else np.nan
    except: return np.nan

inhome['income'] = inhome['a8a'].apply(parse_income)
inhome['lninc'] = np.log(inhome['income'] + 1)
# Winsorize 1% and 99%
p1 = inhome['lninc'].quantile(0.01)
p99 = inhome['lninc'].quantile(0.99)
inhome['lninc_win'] = inhome['lninc'].clip(lower=p1, upper=p99)

# Weight variable
inhome['weight'] = inhome['weight1'].astype(float)

print("Step 6: Calculating Descriptive Statistics...")

# Continuous variables
cont_vars = [
    ('edu_yrs', '被访者受教育年限（年）'),
    ('f_isei', '父亲14岁时职业地位（ISEI-08）'),
    ('f_isei10', '父亲职业地位（ISEI/10）'),
    ('pedu_max', '父母最高受教育年限（年）'),
    ('age', '被访者年龄（岁）'),
    ('f_class14', '14岁时家庭主观阶层（1-10分）'),
    ('income', '个人去年总收入（元）'),
    ('lninc_win', '个人年收入对数（ln(x+1)，1%/99%缩尾）')
]

cont_rows = []
for v, label in cont_vars:
    sub = inhome[[v, 'weight']].dropna()
    w = DescrStatsW(sub[v], weights=sub['weight'], ddof=1)
    cont_rows.append({
        'varname': v,
        'label': label,
        'N': len(sub),
        'mean_raw': sub[v].mean(),
        'sd_raw': sub[v].std(),
        'mean_w': w.mean,
        'sd_w': w.std,
        'min': sub[v].min(),
        'max': sub[v].max()
    })
df_cont_stats = pd.DataFrame(cont_rows)

# Categorical variables
cat_vars = [
    ('comp_jhs', '阶段一：完成初中', {0: '未完成初中（小学及以下）', 1: '完成初中及以上'}),
    ('comp_shs', '阶段二：完成高中（初中毕业子样本）', {0: '初中毕业即止', 1: '完成高中/中职及以上'}),
    ('comp_univ', '阶段三：完成大学（高中毕业子样本）', {0: '高中阶段毕业即止', 1: '完成大专/大学及以上'}),
    ('female', '性别', {0: '男', 1: '女'}),
    ('minority', '民族身份', {0: '汉族', 1: '少数民族'}),
    ('cohort', '出生历史队列', {1: '1960及以前（前改革时代）', 2: '1961-1970（恢复高考初期）', 3: '1971-1980（改革推进期）', 4: '1981-1990（义务教育与扩招期）', 5: '1991及以后（高等教育大众化期）'}),
    ('rural_hukou', '户口登记性质', {0: '非农业户口/居民户口', 1: '农业户口'}),
    ('f_party', '父亲政治面貌', {0: '非中共党员（群众/共青团/民主党派）', 1: '中共党员'})
]

cat_rows = []
for v, vlabel, val_dict in cat_vars:
    sub = inhome[[v, 'weight']].dropna()
    total_raw = len(sub)
    w_sum = sub.groupby(v)['weight'].sum()
    total_w = w_sum.sum()
    
    for val_code, val_name in val_dict.items():
        freq_raw = (sub[v] == val_code).sum()
        pct_raw = (freq_raw / total_raw) * 100
        w_freq = w_sum.get(val_code, 0)
        pct_w = (w_freq / total_w) * 100
        cat_rows.append({
            'varname': v,
            'varlabel': vlabel,
            'category': val_name,
            'cat_code': val_code,
            'N_raw': freq_raw,
            'pct_raw': pct_raw,
            'pct_w': pct_w,
            'total_N': total_raw
        })
df_cat_stats = pd.DataFrame(cat_rows)

print("Step 7: Writing standalone Excel table: 汤晋欢+24307090021_描述统计表.xlsx ...")
with pd.ExcelWriter('汤晋欢+24307090021_描述统计表.xlsx', engine='openpyxl') as writer:
    df_cont_stats.to_excel(writer, sheet_name='连续变量描述统计', index=False)
    df_cat_stats.to_excel(writer, sheet_name='分类变量描述统计', index=False)

print("Excel descriptive table written successfully.")
