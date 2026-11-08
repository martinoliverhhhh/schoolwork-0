/*==============================================================================
课程名称：社会调查实践（定量方向）
作业名称：作业一——变量构造与描述统计
学生姓名：汤晋欢
学生学号：24307090021
研究赛道：赛道一——教育、收入与代际地位获得
复刻文献：唐俊超（2015）《输在起跑线——再议中国社会的教育不平等（1978—2008）》，《社会学研究》第3期
数据来源：中国综合社会调查 CGSS 2023（中国人民大学中国调查与数据中心发布）
原始数据文件：c:/Users/12559/Desktop/CGSS2023/CGSS2023.dta
运行环境：Stata/MP 18.0
==============================================================================*/

clear all
set more off
cap log close

* 设置工作路径
cap cd "c:/Users/12559/Desktop/社会调查实践"

* 开启日志记录
log using "汤晋欢+24307090021_运行日志.log", replace text

di "========================================================================"
di "社会调查实践 作业一 数据处理与分析日志"
di "学生：汤晋欢  学号：24307090021"
di "日期：" c(current_date) "  时间：" c(current_time)
di "Stata版本：" c(stata_version) "  系统类型：" c(os)
di "========================================================================"

*-------------------------------------------------------------------------------
* 第一部分：读取原始数据与样本筛选
*-------------------------------------------------------------------------------
di _newline "【第一步：读取原始数据】"
use "CGSS2023.dta", clear
count
di "CGSS 2023 原始总样本量：" r(N)

di _newline "【第二步：分析样本界定与筛选】"
tab isurban, m
* 说明：CGSS 2023 包含入户面访与电话调查（CATI）。
* 电话调查样本（isurban = -5）未调查家庭背景、父母职业与教育等核心代际分层模块。
* 按照课程规范与代际流动研究标准做法，限定为入户面访有效样本（居委会与村委会）。
keep if isurban == 1 | isurban == 2
count
di "限定入户面访后的分析基准样本量：" r(N)

*-------------------------------------------------------------------------------
* 第二部分：统一缺失值编码处理（-1 至 -5 设为系统缺失值）
*-------------------------------------------------------------------------------
di _newline "【第三步：缺失值统一编码处理】"
* CGSS 标准缺失值：-1(不适用), -2(不知道), -3(拒绝回答), -4(入户面访未调查), -5(电话调查未调查)
local raw_vars a7a a89b a90b isco08f a2 a4 a3a a18 a43d a89c a8a
foreach v of local raw_vars {
    recode `v' (-5/-1 = .)
}

*-------------------------------------------------------------------------------
* 第三部分：因变量构造（Mare 顺序升学转换与受教育年限）
*-------------------------------------------------------------------------------
di _newline "【第四步：因变量构造】"

* 1. 被访者受教育年限（edu_yrs）
* 根据中国学制转换：没有受过任何教育=0，私塾/扫盲班=1，小学=6，初中=9，
* 高中/中专/技校/职高=12，大专=15，大学本科=16，研究生及以上=19，其他=缺失。
gen edu_yrs = .
replace edu_yrs = 0  if a7a == 1
replace edu_yrs = 1  if a7a == 2
replace edu_yrs = 6  if a7a == 3
replace edu_yrs = 9  if a7a == 4
replace edu_yrs = 12 if inlist(a7a, 5, 6, 7, 8)
replace edu_yrs = 15 if inlist(a7a, 9, 10)
replace edu_yrs = 16 if inlist(a7a, 11, 12)
replace edu_yrs = 19 if a7a == 13
label var edu_yrs "被访者受教育年限（年）"

* 2. 被访者最高教育层次分类（edu_level）
gen edu_level = .
replace edu_level = 1 if inlist(a7a, 1, 2, 3)
replace edu_level = 2 if a7a == 4
replace edu_level = 3 if inlist(a7a, 5, 6, 7, 8)
replace edu_level = 4 if inlist(a7a, 9, 10, 11, 12, 13)
label define edulbl 1 "小学及以下" 2 "初中" 3 "高中/中职" 4 "大学及以上"
label values edu_level edulbl
label var edu_level "最高受教育程度层次"

* 3. Mare 顺序升学二元转换变量（复刻唐俊超2015核心设定）
* 转换一：小学升初中（全样本中是否完成初中及以上）
gen comp_jhs = .
replace comp_jhs = 0 if inlist(a7a, 1, 2, 3)
replace comp_jhs = 1 if inlist(a7a, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
label define jhslbl 0 "小学及以下" 1 "初中及以上"
label values comp_jhs jhslbl
label var comp_jhs "阶段一：完成初中（是否升入初中）"

* 转换二：初中升高中（在初中毕业及以上风险人群中，是否完成高中/中职及以上）
gen comp_shs = .
replace comp_shs = 0 if a7a == 4
replace comp_shs = 1 if inlist(a7a, 5, 6, 7, 8, 9, 10, 11, 12, 13)
label define shslbl 0 "初中毕业即止" 1 "高中/中职及以上"
label values comp_shs shslbl
label var comp_shs "阶段二：完成高中（初中毕业生中是否升学）"

* 转换三：高中升大学（在高中毕业及以上风险人群中，是否完成大专/大学及以上）
gen comp_univ = .
replace comp_univ = 0 if inlist(a7a, 5, 6, 7, 8)
replace comp_univ = 1 if inlist(a7a, 9, 10, 11, 12, 13)
label define univlbl 0 "高中毕业即止" 1 "大学及以上"
label values comp_univ univlbl
label var comp_univ "阶段三：完成大学（高中毕业生中是否升学）"

*-------------------------------------------------------------------------------
* 第四部分：核心自变量构造（家庭背景与阶层地位）
*-------------------------------------------------------------------------------
di _newline "【第五步：核心自变量构造】"

* 1. 父亲14岁时职业地位 ISEI 得分（采用 Ganzeboom ISCO-08 转 ISEI 标准量表）
iscogen f_isei = isei(isco08f), from(isco08)
label var f_isei "父亲14岁时职业地位（ISEI-08）"

* 构造进入回归模型的 f_isei10（ISEI除以10，便于解释单位优势比）
gen f_isei10 = f_isei / 10
label var f_isei10 "父亲职业地位（ISEI/10）"

* 2. 父母文化背景（受教育年限）
* 父亲受教育年限（f_edu）
gen f_edu = .
replace f_edu = 0  if a89b == 1
replace f_edu = 1  if a89b == 2
replace f_edu = 6  if a89b == 3
replace f_edu = 9  if a89b == 4
replace f_edu = 12 if inlist(a89b, 5, 6, 7, 8)
replace f_edu = 15 if inlist(a89b, 9, 10)
replace f_edu = 16 if inlist(a89b, 11, 12)
replace f_edu = 19 if a89b == 13
label var f_edu "父亲受教育年限（年）"

* 母亲受教育年限（m_edu）
gen m_edu = .
replace m_edu = 0  if a90b == 1
replace m_edu = 1  if a90b == 2
replace m_edu = 6  if a90b == 3
replace m_edu = 9  if a90b == 4
replace m_edu = 12 if inlist(a90b, 5, 6, 7, 8)
replace m_edu = 15 if inlist(a90b, 9, 10)
replace m_edu = 16 if inlist(a90b, 11, 12)
replace m_edu = 19 if a90b == 13
label var m_edu "母亲受教育年限（年）"

* 父母最高受教育年限（pedu_max = max(f_edu, m_edu)）
egen pedu_max = rowmax(f_edu m_edu)
label var pedu_max "父母最高受教育年限（年）"

*-------------------------------------------------------------------------------
* 第五部分：控制变量与补充变量构造
*-------------------------------------------------------------------------------
di _newline "【第六步：控制变量与补充变量构造】"

* 1. 性别（female）: 1=男, 2=女 -> 0=男, 1=女
gen female = .
replace female = 0 if a2 == 1
replace female = 1 if a2 == 2
label define sexlbl 0 "男" 1 "女"
label values female sexlbl
label var female "性别（女=1）"

* 2. 民族（minority）: 1=汉族, 2-8=少数民族
gen minority = .
replace minority = 0 if a4 == 1
replace minority = 1 if inrange(a4, 2, 8)
label define ethlbl 0 "汉族" 1 "少数民族"
label values minority ethlbl
label var minority "民族身份（少数民族=1）"

* 3. 出生年份与年龄
gen birth_year = a3a
gen age = 2023 - birth_year
label var birth_year "出生年份"
label var age "年龄（岁）"

* 4. 出生历史队列（cohort）
gen cohort = .
replace cohort = 1 if birth_year <= 1960 & birth_year != .
replace cohort = 2 if inrange(birth_year, 1961, 1970)
replace cohort = 3 if inrange(birth_year, 1971, 1980)
replace cohort = 4 if inrange(birth_year, 1981, 1990)
replace cohort = 5 if birth_year >= 1991 & birth_year != .
label define cohortlbl 1 "1960及以前" 2 "1961-1970" 3 "1971-1980" 4 "1981-1990" 5 "1991及以后"
label values cohort cohortlbl
label var cohort "出生历史队列"

* 5. 户口登记状况（rural_hukou）: 1=农业户口, 2-5=非农/居民/军籍, 6-7=其他/无户口(设缺失)
gen rural_hukou = .
replace rural_hukou = 1 if a18 == 1
replace rural_hukou = 0 if inlist(a18, 2, 3, 4, 5)
label define hukoulbl 0 "非农业/居民户口" 1 "农业户口"
label values rural_hukou hukoulbl
label var rural_hukou "户口登记性质（农业户口=1）"

* 6. 14岁时家庭主观社会阶层（f_class14）: 原始 1-10分
gen f_class14 = a43d if inrange(a43d, 1, 10)
label var f_class14 "14岁时家庭主观阶层认同（1-10分）"

* 7. 父亲政治面貌（f_party）: 1=群众, 2=共青团员, 3=民主党派, 4=共产党员
gen f_party = .
replace f_party = 0 if inlist(a89c, 1, 2, 3)
replace f_party = 1 if a89c == 4
label define partylbl 0 "非中共党员" 1 "中共党员"
label values f_party partylbl
label var f_party "父亲政治面貌（中共党员=1）"

* 8. 收入变量构造（个人年收入对数与缩尾处理，作业评分重点考察项）
* a8a 处理：负值已设缺失；9999996为100万元及以上（赋值1,000,000）；
* 9999997-9999999为不知道/无法回答，设缺失。
gen income = a8a
replace income = 1000000 if a8a == 9999996
replace income = . if inlist(a8a, 9999997, 9999998, 9999999)
replace income = . if income < 0
label var income "个人去年总收入（元）"

* 对数处理：ln(x + 1)，避免零收入丢失
gen lninc = ln(income + 1)
label var lninc "个人年收入对数 ln(x+1)"

* 双侧 1% 与 99% 缩尾处理（Winsorization）
_pctile lninc, p(1 99)
gen lninc_win = lninc
replace lninc_win = r(r1) if lninc < r(r1) & lninc != .
replace lninc_win = r(r2) if lninc > r(r2) & lninc != .
label var lninc_win "个人年收入对数（1%/99%缩尾）"

* 9. 权重变量设置
gen weight = weight1
label var weight "个人层级抽样权重"

*-------------------------------------------------------------------------------
* 第六部分：完整描述统计展示（连续变量与分类变量，未加权与加权）
*-------------------------------------------------------------------------------
di _newline "========================================================================"
di "【第七步：连续变量描述统计（未加权）】"
di "========================================================================"
summarize edu_yrs f_isei f_isei10 f_edu m_edu pedu_max age f_class14 income lninc lninc_win, detail

di _newline "========================================================================"
di "【第八步：连续变量描述统计（使用个人抽样权重 weight1）】"
di "========================================================================"
summarize edu_yrs f_isei f_isei10 f_edu m_edu pedu_max age f_class14 income lninc lninc_win [aweight = weight]

di _newline "========================================================================"
di "【第九步：分类变量频数与百分比统计（未加权）】"
di "========================================================================"
tab1 comp_jhs comp_shs comp_univ edu_level female minority cohort rural_hukou f_party, m

di _newline "========================================================================"
di "【第十步：分类变量加权分布统计（使用个人抽样权重 weight1）】"
di "========================================================================"
foreach v in comp_jhs comp_shs comp_univ edu_level female minority cohort rural_hukou f_party {
    di _newline "--- 加权分布: `v' ---"
    tab `v' [iweight = weight]
}

*-------------------------------------------------------------------------------
* 第七部分：基准回归模型拟合（验证研究设计与变量有效性）
* 估计 Mare 顺序 Logit 升学模型：阶段一（初中）、阶段二（高中）、阶段三（大学）
*-------------------------------------------------------------------------------
di _newline "========================================================================"
di "【第十一步：基准升学模型估计（Mare 顺序二元 Logit 转换）】"
di "========================================================================"

di _newline ">>> 模型 1：完成初中（全样本风险人群）<<<"
logit comp_jhs f_isei10 pedu_max female minority i.cohort rural_hukou f_class14 f_party
estimates store m_jhs
logit, or

di _newline ">>> 模型 2：完成高中（初中毕业风险人群子样本）<<<"
logit comp_shs f_isei10 pedu_max female minority i.cohort rural_hukou f_class14 f_party if comp_jhs == 1
estimates store m_shs
logit, or

di _newline ">>> 模型 3：完成大学（高中毕业风险人群子样本）<<<"
logit comp_univ f_isei10 pedu_max female minority i.cohort rural_hukou f_class14 f_party if comp_shs == 1
estimates store m_univ
logit, or

di _newline "========================================================================"
di "【数据处理与模型运行完毕】"
di "========================================================================"

log close
exit, clear
