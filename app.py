import base64
import streamlit as st
import json
import os
import hashlib
import copy
import time

# 尝试导入 logic 模块中的版本号，如果 logic.py 里没有定义 VERSION，则使用默认值
try:
    from logic import WorkplaceOptimizer
    from logic import VERSION as LOGIC_VERSION
except ImportError:
    from logic import WorkplaceOptimizer

    LOGIC_VERSION = "1.0.0"

# ==========================================
# 版本控制配置
# ==========================================
APP_VERSION = "2.0.0"  # 在此处修改前端 App 版本号

# ==========================================
# 本地资源配置
# ==========================================

# 1. 建立干员名称与 ID 的映射表
RAW_OPS_DATA = [
    {"id": "char_002_amiya", "name": "阿米娅"}, {"id": "char_003_kalts", "name": "凯尔希"},
    {"id": "char_009_12fce", "name": "12F"}, {"id": "char_010_chen", "name": "陈"},
    {"id": "char_017_huang", "name": "煌"}, {"id": "char_1011_lava2", "name": "炎狱炎熔"},
    {"id": "char_1012_skadi2", "name": "浊心斯卡蒂"}, {"id": "char_1013_chen2", "name": "假日威龙陈"},
    {"id": "char_1014_nearl2", "name": "耀骑士临光"}, {"id": "char_1016_agoat2", "name": "纯烬艾雅法拉"},
    {"id": "char_1019_siege2", "name": "维娜·维多利亚"}, {"id": "char_101_sora", "name": "空"},
    {"id": "char_1020_reed2", "name": "焰影苇草"}, {"id": "char_1021_kroos2", "name": "寒芒克洛丝"},
    {"id": "char_1023_ghost2", "name": "归溟幽灵鲨"}, {"id": "char_1024_hbisc2", "name": "濯尘芙蓉"},
    {"id": "char_1026_gvial2", "name": "百炼嘉维尔"}, {"id": "char_1027_greyy2", "name": "承曦格雷伊"},
    {"id": "char_1028_texas2", "name": "缄默德克萨斯"}, {"id": "char_1029_yato2", "name": "麒麟R夜刀"},
    {"id": "char_102_texas", "name": "德克萨斯"}, {"id": "char_1030_noirc2", "name": "火龙S黑角"},
    {"id": "char_1031_slent2", "name": "淬羽赫默"}, {"id": "char_1032_excu2", "name": "圣约送葬人"},
    {"id": "char_1033_swire2", "name": "琳琅诗怀雅"}, {"id": "char_1034_jesca2", "name": "涤火杰西卡"},
    {"id": "char_1035_wisdel", "name": "维什戴尔"}, {"id": "char_1036_fang2", "name": "历阵锐枪芬"},
    {"id": "char_1038_whitw2", "name": "荒芜拉普兰德"}, {"id": "char_1039_thorn2", "name": "引星棘刺"},
    {"id": "char_103_angel", "name": "能天使"}, {"id": "char_1040_blaze2", "name": "烛煌"},
    {"id": "char_1041_angel2", "name": "新约能天使"}, {"id": "char_1042_phatm2", "name": "酒神"},
    {"id": "char_1043_leizi2", "name": "司霆惊蛰"}, {"id": "char_1044_hsgma2", "name": "斩业星熊"},
    {"id": "char_1045_svash2", "name": "凛御银灰"}, {"id": "char_1046_sbell2", "name": "圣聆初雪"},
    {"id": "char_1047_halo2", "name": "溯光星源"}, {"id": "char_106_franka", "name": "芙兰卡"},
    {"id": "char_107_liskam", "name": "雷蛇"}, {"id": "char_108_silent", "name": "赫默"},
    {"id": "char_109_fmout", "name": "远山"}, {"id": "char_110_deepcl", "name": "深海色"},
    {"id": "char_112_siege", "name": "推进之王"}, {"id": "char_113_cqbw", "name": "W"},
    {"id": "char_115_headbr", "name": "凛冬"}, {"id": "char_117_myrrh", "name": "末药"},
    {"id": "char_118_yuki", "name": "白雪"}, {"id": "char_120_hibisc", "name": "芙蓉"},
    {"id": "char_121_lava", "name": "炎熔"}, {"id": "char_122_beagle", "name": "米格鲁"},
    {"id": "char_123_fang", "name": "芬"}, {"id": "char_124_kroos", "name": "克洛丝"},
    {"id": "char_126_shotst", "name": "流星"}, {"id": "char_127_estell", "name": "艾丝黛尔"},
    {"id": "char_128_plosis", "name": "白面鸮"}, {"id": "char_129_bluep", "name": "蓝毒"},
    {"id": "char_130_doberm", "name": "杜宾"}, {"id": "char_131_flameb", "name": "炎客"},
    {"id": "char_133_mm", "name": "梅"}, {"id": "char_134_ifrit", "name": "伊芙利特"},
    {"id": "char_135_halo", "name": "星源"}, {"id": "char_136_hsguma", "name": "星熊"},
    {"id": "char_137_brownb", "name": "猎蜂"}, {"id": "char_140_whitew", "name": "拉普兰德"},
    {"id": "char_141_nights", "name": "夜烟"}, {"id": "char_143_ghost", "name": "幽灵鲨"},
    {"id": "char_144_red", "name": "红"}, {"id": "char_145_prove", "name": "普罗旺斯"},
    {"id": "char_147_shining", "name": "闪灵"}, {"id": "char_148_nearl", "name": "临光"},
    {"id": "char_149_scave", "name": "清道夫"}, {"id": "char_1502_crosly", "name": "弑君者"},
    {"id": "char_150_snakek", "name": "蛇屠箱"}, {"id": "char_151_myrtle", "name": "桃金娘"},
    {"id": "char_154_morgan", "name": "摩根"}, {"id": "char_155_tiger", "name": "因陀罗"},
    {"id": "char_157_dagda", "name": "达格达"}, {"id": "char_158_milu", "name": "守林人"},
    {"id": "char_159_peacok", "name": "断罪者"}, {"id": "char_163_hpsts", "name": "火神"},
    {"id": "char_164_nightm", "name": "夜魔"}, {"id": "char_166_skfire", "name": "天火"},
    {"id": "char_171_bldsk", "name": "华法琳"}, {"id": "char_172_svrash", "name": "银灰"},
    {"id": "char_173_slchan", "name": "崖心"}, {"id": "char_174_slbell", "name": "初雪"},
    {"id": "char_179_cgbird", "name": "夜莺"}, {"id": "char_180_amgoat", "name": "艾雅法拉"},
    {"id": "char_181_flower", "name": "调香师"}, {"id": "char_183_skgoat", "name": "地灵"},
    {"id": "char_185_frncat", "name": "慕斯"}, {"id": "char_187_ccheal", "name": "嘉维尔"},
    {"id": "char_188_helage", "name": "赫拉格"}, {"id": "char_190_clour", "name": "红云"},
    {"id": "char_192_falco", "name": "翎羽"}, {"id": "char_193_frostl", "name": "霜叶"},
    {"id": "char_194_leto", "name": "烈夏"}, {"id": "char_195_glassb", "name": "真理"},
    {"id": "char_196_sunbr", "name": "古米"}, {"id": "char_197_poca", "name": "早露"},
    {"id": "char_198_blackd", "name": "讯使"}, {"id": "char_199_yak", "name": "角峰"},
    {"id": "char_2012_typhon", "name": "提丰"}, {"id": "char_2013_cerber", "name": "刻俄柏"},
    {"id": "char_2014_nian", "name": "年"}, {"id": "char_2015_dusk", "name": "夕"},
    {"id": "char_201_moeshd", "name": "可颂"}, {"id": "char_2023_ling", "name": "令"},
    {"id": "char_2024_chyue", "name": "重岳"}, {"id": "char_2025_shu", "name": "黍"},
    {"id": "char_2026_yu", "name": "余"}, {"id": "char_202_demkni", "name": "塞雷娅"},
    {"id": "char_204_platnm", "name": "白金"}, {"id": "char_206_gnosis", "name": "灵知"},
    {"id": "char_208_melan", "name": "玫兰莎"}, {"id": "char_209_ardign", "name": "卡缇"},
    {"id": "char_210_stward", "name": "史都华德"}, {"id": "char_211_adnach", "name": "安德切尔"},
    {"id": "char_212_ansel", "name": "安赛尔"}, {"id": "char_213_mostma", "name": "莫斯提马"},
    {"id": "char_214_kafka", "name": "卡夫卡"}, {"id": "char_215_mantic", "name": "狮蝎"},
    {"id": "char_218_cuttle", "name": "安哲拉"}, {"id": "char_219_meteo", "name": "陨星"},
    {"id": "char_220_grani", "name": "格拉尼"}, {"id": "char_222_bpipe", "name": "风笛"},
    {"id": "char_225_haak", "name": "阿"}, {"id": "char_226_hmau", "name": "吽"},
    {"id": "char_230_savage", "name": "暴行"}, {"id": "char_235_jesica", "name": "杰西卡"},
    {"id": "char_236_rope", "name": "暗索"}, {"id": "char_237_gravel", "name": "砾"},
    {"id": "char_240_wyvern", "name": "香草"}, {"id": "char_241_panda", "name": "食铁兽"},
    {"id": "char_242_otter", "name": "梅尔"}, {"id": "char_243_waaifu", "name": "槐琥"},
    {"id": "char_245_cello", "name": "塑心"}, {"id": "char_248_mgllan", "name": "麦哲伦"},
    {"id": "char_249_mlyss", "name": "缪尔赛思"}, {"id": "char_250_phatom", "name": "傀影"},
    {"id": "char_252_bibeak", "name": "柏喙"}, {"id": "char_253_greyy", "name": "格雷伊"},
    {"id": "char_254_vodfox", "name": "巫恋"}, {"id": "char_258_podego", "name": "波登可"},
    {"id": "char_260_durnar", "name": "坚雷"}, {"id": "char_261_sddrag", "name": "苇草"},
    {"id": "char_263_skadi", "name": "斯卡蒂"}, {"id": "char_264_f12yin", "name": "山"},
    {"id": "char_265_sophia", "name": "鞭刃"}, {"id": "char_271_spikes", "name": "芳汀"},
    {"id": "char_272_strong", "name": "孑"}, {"id": "char_274_astesi", "name": "星极"},
    {"id": "char_275_breeze", "name": "微风"}, {"id": "char_277_sqrrel", "name": "阿消"},
    {"id": "char_278_orchid", "name": "梓兰"}, {"id": "char_279_excu", "name": "送葬人"},
    {"id": "char_281_popka", "name": "泡普卡"}, {"id": "char_282_catap", "name": "空爆"},
    {"id": "char_283_midn", "name": "月见夜"}, {"id": "char_284_spot", "name": "斑点"},
    {"id": "char_285_medic2", "name": "Lancet-2"}, {"id": "char_286_cast3", "name": "Castle-3"},
    {"id": "char_289_gyuki", "name": "缠丸"}, {"id": "char_290_vigna", "name": "红豆"},
    {"id": "char_291_aglina", "name": "安洁莉娜"}, {"id": "char_293_thorns", "name": "棘刺"},
    {"id": "char_294_ayer", "name": "断崖"}, {"id": "char_297_hamoni", "name": "和弦"},
    {"id": "char_298_susuro", "name": "苏苏洛"}, {"id": "char_300_phenxi", "name": "菲亚梅塔"},
    {"id": "char_301_cutter", "name": "刻刀"}, {"id": "char_302_glaze", "name": "安比尔"},
    {"id": "char_304_zebra", "name": "暴雨"}, {"id": "char_306_leizi", "name": "惊蛰"},
    {"id": "char_308_swire", "name": "诗怀雅"}, {"id": "char_311_mudrok", "name": "泥岩"},
    {"id": "char_322_lmlee", "name": "老鲤"}, {"id": "char_325_bison", "name": "拜松"},
    {"id": "char_326_glacus", "name": "格劳克斯"}, {"id": "char_328_cammou", "name": "卡达"},
    {"id": "char_332_archet", "name": "空弦"}, {"id": "char_333_sidero", "name": "铸铁"},
    {"id": "char_336_folivo", "name": "稀音"}, {"id": "char_337_utage", "name": "宴"},
    {"id": "char_338_iris", "name": "爱丽丝"}, {"id": "char_340_shwaz", "name": "黑"},
    {"id": "char_341_sntlla", "name": "寒檀"}, {"id": "char_343_tknogi", "name": "月禾"},
    {"id": "char_344_beewax", "name": "蜜蜡"}, {"id": "char_345_folnic", "name": "亚叶"},
    {"id": "char_346_aosta", "name": "奥斯塔"}, {"id": "char_347_jaksel", "name": "杰克"},
    {"id": "char_348_ceylon", "name": "锡兰"}, {"id": "char_349_chiave", "name": "贾维"},
    {"id": "char_350_surtr", "name": "史尔特尔"}, {"id": "char_355_ethan", "name": "伊桑"},
    {"id": "char_356_broca", "name": "布洛卡"}, {"id": "char_358_lisa", "name": "铃兰"},
    {"id": "char_362_saga", "name": "嵯峨"}, {"id": "char_363_toddi", "name": "熔泉"},
    {"id": "char_365_aprl", "name": "四月"}, {"id": "char_366_acdrop", "name": "酸糖"},
    {"id": "char_367_swllow", "name": "灰喉"}, {"id": "char_369_bena", "name": "贝娜"},
    {"id": "char_373_lionhd", "name": "莱恩哈特"}, {"id": "char_376_therex", "name": "THRM-EX"},
    {"id": "char_377_gdglow", "name": "澄闪"}, {"id": "char_378_asbest", "name": "石棉"},
    {"id": "char_379_sesa", "name": "慑砂"}, {"id": "char_381_bubble", "name": "泡泡"},
    {"id": "char_383_snsant", "name": "雪雉"}, {"id": "char_385_finlpp", "name": "清流"},
    {"id": "char_388_mint", "name": "薄绿"}, {"id": "char_391_rosmon", "name": "迷迭香"},
    {"id": "char_394_hadiya", "name": "哈蒂娅"}, {"id": "char_4000_jnight", "name": "正义骑士号"},
    {"id": "char_4004_pudd", "name": "布丁"}, {"id": "char_4006_melnte", "name": "玫拉"},
    {"id": "char_4009_irene", "name": "艾丽妮"}, {"id": "char_400_weedy", "name": "温蒂"},
    {"id": "char_4010_etlchi", "name": "隐德来希"}, {"id": "char_4011_lessng", "name": "止颂"},
    {"id": "char_4013_kjera", "name": "耶拉"}, {"id": "char_4014_lunacu", "name": "子月"},
    {"id": "char_4015_spuria", "name": "空构"}, {"id": "char_4016_kazema", "name": "风丸"},
    {"id": "char_4017_puzzle", "name": "谜图"}, {"id": "char_4019_ncdeer", "name": "九色鹿"},
    {"id": "char_401_elysm", "name": "极境"}, {"id": "char_4023_rfalcn", "name": "红隼"},
    {"id": "char_4025_aprot2", "name": "暮落"}, {"id": "char_4026_vulpis", "name": "忍冬"},
    {"id": "char_4027_heyak", "name": "霍尔海雅"}, {"id": "char_402_tuye", "name": "图耶"},
    {"id": "char_4032_provs", "name": "但书"}, {"id": "char_4036_forcer", "name": "见行者"},
    {"id": "char_4039_horn", "name": "号角"}, {"id": "char_4040_rockr", "name": "洛洛"},
    {"id": "char_4041_chnut", "name": "褐果"}, {"id": "char_4042_lumen", "name": "流明"},
    {"id": "char_4043_erato", "name": "埃拉托"}, {"id": "char_4045_heidi", "name": "海蒂"},
    {"id": "char_4046_ebnhlz", "name": "黑键"}, {"id": "char_4047_pianst", "name": "车尔尼"},
    {"id": "char_4048_doroth", "name": "多萝西"}, {"id": "char_4051_akkord", "name": "协律"},
    {"id": "char_4052_surfer", "name": "寻澜"}, {"id": "char_4054_malist", "name": "至简"},
    {"id": "char_4055_bgsnow", "name": "鸿雪"}, {"id": "char_4058_pepe", "name": "佩佩"},
    {"id": "char_405_absin", "name": "苦艾"}, {"id": "char_4062_totter", "name": "铅踝"},
    {"id": "char_4063_quartz", "name": "石英"}, {"id": "char_4064_mlynar", "name": "玛恩纳"},
    {"id": "char_4065_judge", "name": "斥罪"}, {"id": "char_4066_highmo", "name": "海沫"},
    {"id": "char_4067_lolxh", "name": "罗小黑"}, {"id": "char_4071_peper", "name": "明椒"},
    {"id": "char_4072_ironmn", "name": "白铁"}, {"id": "char_4077_palico", "name": "泰拉大陆调查团"},
    {"id": "char_4078_bdhkgt", "name": "截云"}, {"id": "char_4079_haini", "name": "海霓"},
    {"id": "char_4080_lin", "name": "林"}, {"id": "char_4081_warmy", "name": "温米"},
    {"id": "char_4082_qiubai", "name": "仇白"}, {"id": "char_4083_chimes", "name": "铎铃"},
    {"id": "char_4087_ines", "name": "伊内丝"}, {"id": "char_4088_hodrer", "name": "赫德雷"},
    {"id": "char_4091_ulika", "name": "U-Official"}, {"id": "char_4093_frston", "name": "Friston-3"},
    {"id": "char_4098_vvana", "name": "薇薇安娜"}, {"id": "char_4100_caper", "name": "跃跃"},
    {"id": "char_4102_threye", "name": "凛视"}, {"id": "char_4104_coldst", "name": "冰酿"},
    {"id": "char_4105_almond", "name": "杏仁"}, {"id": "char_4106_bryota", "name": "苍苔"},
    {"id": "char_4107_vrdant", "name": "维荻"}, {"id": "char_4109_baslin", "name": "深律"},
    {"id": "char_4110_delphn", "name": "戴菲恩"}, {"id": "char_4114_harold", "name": "哈洛德"},
    {"id": "char_4116_blkkgt", "name": "锏"}, {"id": "char_4117_ray", "name": "莱伊"},
    {"id": "char_4119_wanqin", "name": "万顷"}, {"id": "char_411_tomimi", "name": "特米米"},
    {"id": "char_4121_zuole", "name": "左乐"}, {"id": "char_4122_grabds", "name": "小满"},
    {"id": "char_4123_ela", "name": "艾拉"}, {"id": "char_4124_iana", "name": "双月"},
    {"id": "char_4125_rdoc", "name": "医生"}, {"id": "char_4126_fuze", "name": "导火索"},
    {"id": "char_4130_luton", "name": "露托"}, {"id": "char_4131_odda", "name": "奥达"},
    {"id": "char_4132_ascln", "name": "阿斯卡纶"}, {"id": "char_4133_logos", "name": "逻各斯"},
    {"id": "char_4134_cetsyr", "name": "魔王"}, {"id": "char_4136_phonor", "name": "PhonoR-0"},
    {"id": "char_4137_udflow", "name": "深巡"}, {"id": "char_4138_narant", "name": "娜仁图亚"},
    {"id": "char_4139_papyrs", "name": "莎草"}, {"id": "char_4140_lasher", "name": "衡沙"},
    {"id": "char_4141_marcil", "name": "玛露西尔"}, {"id": "char_4142_laios", "name": "莱欧斯"},
    {"id": "char_4143_sensi", "name": "森西"}, {"id": "char_4144_chilc", "name": "齐尔查克"},
    {"id": "char_4145_ulpia", "name": "乌尔比安"}, {"id": "char_4146_nymph", "name": "妮芙"},
    {"id": "char_4147_mitm", "name": "渡桥"}, {"id": "char_4148_philae", "name": "菲莱"},
    {"id": "char_4151_tinman", "name": "锡人"}, {"id": "char_4155_talr", "name": "裁度"},
    {"id": "char_415_flint", "name": "燧石"}, {"id": "char_4162_cathy", "name": "凯瑟琳"},
    {"id": "char_4163_rosesa", "name": "瑰盐"}, {"id": "char_4164_tecno", "name": "特克诺"},
    {"id": "char_4165_ctrail", "name": "云迹"}, {"id": "char_416_zumama", "name": "森蚺"},
    {"id": "char_4171_wulfen", "name": "钼铅"}, {"id": "char_4172_xingzh", "name": "行箸"},
    {"id": "char_4173_nowell", "name": "诺威尔"}, {"id": "char_4177_brigid", "name": "水灯心"},
    {"id": "char_4178_alanna", "name": "阿兰娜"}, {"id": "char_4179_monstr", "name": "Mon3tr"},
    {"id": "char_4182_oblvns", "name": "丰川祥子"}, {"id": "char_4183_mortis", "name": "若叶睦"},
    {"id": "char_4184_dolris", "name": "三角初华"}, {"id": "char_4185_amoris", "name": "祐天寺若麦"},
    {"id": "char_4186_tmoris", "name": "八幡海铃"}, {"id": "char_4187_graceb", "name": "聆音"},
    {"id": "char_4188_confes", "name": "CONFESS-47"}, {"id": "char_4191_tippi", "name": "蒂比"},
    {"id": "char_4193_lemuen", "name": "蕾缪安"}, {"id": "char_4194_rmixer", "name": "信仰搅拌机"},
    {"id": "char_4195_radian", "name": "电弧"}, {"id": "char_4196_reckpr", "name": "录武官"},
    {"id": "char_4198_christ", "name": "Miss.Christine"}, {"id": "char_4199_makiri", "name": "松桐"},
    {"id": "char_4202_haruka", "name": "遥"}, {"id": "char_4203_kichi", "name": "吉星"},
    {"id": "char_4204_mantra", "name": "真言"}, {"id": "char_4207_branch", "name": "折桠"},
    {"id": "char_4208_wintim", "name": "冬时"}, {"id": "char_420_flamtl", "name": "焰尾"},
    {"id": "char_4211_snhunt", "name": "雪猎"}, {"id": "char_421_crow", "name": "羽毛笔"},
    {"id": "char_422_aurora", "name": "极光"}, {"id": "char_423_blemsh", "name": "瑕光"},
    {"id": "char_426_billro", "name": "卡涅利安"}, {"id": "char_427_vigil", "name": "伺夜"},
    {"id": "char_430_fartth", "name": "远牙"}, {"id": "char_431_ashlok", "name": "灰毫"},
    {"id": "char_433_windft", "name": "掠风"}, {"id": "char_436_whispr", "name": "絮雨"},
    {"id": "char_437_mizuki", "name": "水月"}, {"id": "char_440_pinecn", "name": "松果"},
    {"id": "char_445_wscoot", "name": "骋风"}, {"id": "char_446_aroma", "name": "阿罗玛"},
    {"id": "char_449_glider", "name": "蜜莓"}, {"id": "char_450_necras", "name": "死芒"},
    {"id": "char_451_robin", "name": "罗宾"}, {"id": "char_452_bstalk", "name": "豆苗"},
    {"id": "char_455_nothin", "name": "乌有"}, {"id": "char_456_ash", "name": "灰烬"},
    {"id": "char_457_blitz", "name": "闪击"}, {"id": "char_458_rfrost", "name": "霜华"},
    {"id": "char_459_tachak", "name": "战车"}, {"id": "char_464_cement", "name": "洋灰"},
    {"id": "char_466_qanik", "name": "雪绒"}, {"id": "char_469_indigo", "name": "深靛"},
    {"id": "char_472_pasngr", "name": "异客"}, {"id": "char_473_mberry", "name": "桑葚"},
    {"id": "char_474_glady", "name": "歌蕾蒂娅"}, {"id": "char_475_akafyu", "name": "赤冬"},
    {"id": "char_476_blkngt", "name": "夜半"}, {"id": "char_478_kirara", "name": "绮良"},
    {"id": "char_479_sleach", "name": "琴柳"}, {"id": "char_484_robrta", "name": "罗比菈塔"},
    {"id": "char_485_pallas", "name": "帕拉斯"}, {"id": "char_486_takila", "name": "龙舌兰"},
    {"id": "char_487_bobb", "name": "波卜"}, {"id": "char_488_buildr", "name": "青枳"},
    {"id": "char_489_serum", "name": "蚀清"}, {"id": "char_491_humus", "name": "休谟斯"},
    {"id": "char_492_quercu", "name": "夏栎"}, {"id": "char_493_firwhl", "name": "火哨"},
    {"id": "char_494_vendla", "name": "刺玫"}, {"id": "char_496_wildmn", "name": "野鬃"},
    {"id": "char_497_ctable", "name": "晓歌"}, {"id": "char_498_inside", "name": "隐现"},
    {"id": "char_499_kaitou", "name": "折光"}, {"id": "char_500_noirc", "name": "黑角"},
    {"id": "char_501_durin", "name": "杜林"}, {"id": "char_502_nblade", "name": "夜刀"},
    {"id": "char_503_rang", "name": "巡林者"}
]

# 生成 名字 -> ID 的快速查询字典
NAME_TO_ID = {op['name']: op['id'] for op in RAW_OPS_DATA}


# 2. 读取本地图片并转 Base64 的函数
def get_avatar_base64(char_id):
    """
    根据 char_id 从 webp96 文件夹读取图片，返回 Base64 字符串。
    如果找不到文件，返回空字符串。
    """
    if not char_id:
        return ""

    # 定义图片文件夹路径 (假设 webp96 文件夹在 app.py 同级目录下)
    img_folder = "webp96"

    file_path = os.path.join(img_folder, f"{char_id}.webp")


    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                encoded = base64.b64encode(data).decode('utf-8')
                # 返回完整的 Data URI Scheme
                return f"data:image/webp;base64,{encoded}"
        except Exception:
            return ""

    return ""


# 3. 智能获取 ID 的函数 (数据缺失时的容错)
def get_real_id(op_item):
    """优先取 item 里的 id，没有则通过 name 查表"""
    # 1. 尝试直接获取 id
    op_id = op_item.get('id')
    if op_id:
        return op_id

    # 2. 如果没有 id，尝试用 name 查表
    name = op_item.get('name')
    if name and name in NAME_TO_ID:
        return NAME_TO_ID[name]

    return None

# ==========================================
# 0. 样式与配置
# ==========================================

st.set_page_config(page_title="MAA 基建排班售后服务", page_icon="💎", layout="wide")

st.markdown("""
<style>
/* 隐藏顶部菜单和页脚 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stAppHeader {display: none;}

/* 卡片样式 */
.user-card {
    padding: 20px;
    background-color: #f0f2f6;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* 强制隐藏右上角 */
.stAppHeader .stToolbarActions .stToolbarActionButton button,
[data-testid="stToolbarActionButtonIcon"],
.stAppHeader .stToolbarActions {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
    gap: 0 !important;
}

/* 优化按钮样式 */
div.stButton > button:first-child {
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 1. 工具函数
# ==========================================

def get_user_hash(order_id):
    return hashlib.sha256(order_id.strip().encode('utf-8')).hexdigest()[:16]


def load_user_data(user_hash):
    base_path = os.path.join("user_data", user_hash)
    ops_path = os.path.join(base_path, "operators.json")
    conf_path = os.path.join(base_path, "config.json")

    if os.path.exists(ops_path) and os.path.exists(conf_path):
        with open(ops_path, 'r', encoding='utf-8') as f:
            ops = json.load(f)
        with open(conf_path, 'r', encoding='utf-8') as f:
            conf = json.load(f)
        return ops, conf
    return None, None


def save_user_data(user_hash, ops_data):
    base_path = os.path.join("user_data", user_hash)
    ops_path = os.path.join(base_path, "operators.json")

    if os.path.exists(base_path):
        with open(ops_path, 'w', encoding='utf-8') as f:
            json.dump(ops_data, f, ensure_ascii=False, indent=2)
        return True
    return False


def upgrade_operator_in_memory(operators_data, char_id, char_name, target_elite):
    """内存修改干员练度"""
    target_id_str = str(char_id)
    for op in operators_data:
        current_id_str = str(op.get('id', ''))
        current_name = op.get('name', '')

        match = False
        if current_id_str and current_id_str == target_id_str:
            match = True
        elif current_name and current_name == char_name:
            match = True

        if match:
            op['elite'] = int(target_elite)
            op['level'] = 1  # 默认重置为1级，根据需求调整
            return True, f"{current_name}"

    return False, None


def clean_data(d):
    return {k: v for k, v in d.items() if k != 'raw_results'}


# ==========================================
# 2. 会话状态初始化
# ==========================================

if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False
if 'user_hash' not in st.session_state:
    st.session_state.user_hash = ""
if 'user_ops' not in st.session_state:
    st.session_state.user_ops = None
if 'user_conf' not in st.session_state:
    st.session_state.user_conf = None
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []
if 'list_version' not in st.session_state:
    st.session_state.list_version = 0
if 'final_result_ready' not in st.session_state:
    st.session_state.final_result_ready = False

# ==========================================
# 3. 登录页
# ==========================================

if not st.session_state.auth_status:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        # st.image(
        #     "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Arknights_logo.svg/1200px-Arknights_logo.svg.png",
        #     width=150)
        st.markdown("<h2 style='text-align: center;'>💎 VIP 基建售后服务</h2>", unsafe_allow_html=True)

        with st.form("login_form"):
            order_id = st.text_input("请输入闲鱼订单号", placeholder="例如：36281xxxxxx")
            submitted = st.form_submit_button("验证身份", use_container_width=True)

            if submitted and order_id:
                u_hash = get_user_hash(order_id)
                ops, conf = load_user_data(u_hash)

                if ops and conf:
                    st.session_state.auth_status = True
                    st.session_state.user_hash = u_hash
                    st.session_state.user_ops = ops
                    st.session_state.user_conf = conf
                    st.toast("✅ 验证成功！", icon="🎉")
                    st.rerun()
                else:
                    st.error("❌ 未找到订单信息或服务已过期，请联系卖家。")

# ==========================================
# 4. 主功能区
# ==========================================

else:
    # --- 侧边栏 ---
    with st.sidebar:
        st.success(f"状态: 已登录")
        st.caption(f"ID: {st.session_state.user_hash[:8]}...")
        st.caption(f"配置: {st.session_state.user_conf.get('desc', 'Custom')}")

        st.divider()

        # --- 新增：版本信息显示 ---
        st.markdown(f"""
        <div style="
            display: flex; 
            justify-content: space-between; 
            color: #666; 
            font-size: 0.8rem;
            margin-bottom: 10px;
        ">
            <span>App: v{APP_VERSION}</span>
            <span>Logic: v{LOGIC_VERSION}</span>
        </div>
        """, unsafe_allow_html=True)
        # ------------------------

        if st.button("退出登录", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.title("🏭 智能排班生成器")

    # --- 逻辑控制区 ---

    # 临时文件路径定义
    temp_ops_path = f"temp_{st.session_state.user_hash}.json"
    temp_conf_path = f"temp_conf_{st.session_state.user_hash}.json"

    # 1. 自动运行分析 (如果是首次加载或数据已更新)
    if not st.session_state.analysis_done:
        with st.status("正在分析基建潜力...", expanded=True) as status:
            try:
                # 写入临时文件供算法读取
                with open(temp_ops_path, "w", encoding='utf-8') as f:
                    json.dump(st.session_state.user_ops, f)
                with open(temp_conf_path, "w", encoding='utf-8') as f:
                    json.dump(st.session_state.user_conf, f)

                # 调用核心算法
                optimizer = WorkplaceOptimizer("internal", temp_ops_path, temp_conf_path)
                curr = optimizer.get_optimal_assignments(ignore_elite=False)
                pot = optimizer.get_optimal_assignments(ignore_elite=True)
                upgrades = optimizer.calculate_upgrade_requirements(curr, pot)

                st.session_state.suggestions = upgrades
                st.session_state.analysis_done = True
                status.update(label="✅ 分析完成", state="complete", expanded=False)

                # 分析完成后刷新显示
                st.rerun()

            except Exception as e:
                status.update(label="❌ 分析出错", state="error")
                st.error(f"算法错误: {str(e)}")
                st.stop()

    # 2. 如果已有结果，优先展示下载区 (放在顶部更方便)
    if st.session_state.get('final_result_ready', False):
        st.markdown("### 🎉 排班表已生成")
        result_container = st.container(border=True)
        with result_container:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.metric("预计最终效率", f"{st.session_state.final_eff:.2f}")
            with c2:
                st.download_button(
                    label="📥 下载 MAA 排班 JSON",
                    data=st.session_state.final_result_json,
                    file_name="maa_schedule_optimized.json",
                    mime="application/json",
                    type="primary",
                    use_container_width=True
                )
            st.caption("注：此文件包含您刚才勾选并应用的练度修改。")

    # ==========================================
    # 优化后的：3. 练度建议交互区
    # ==========================================
    st.markdown("### 🛠️ 练度优化建议")


    # --- 辅助函数：获取头像 URL ---
    def get_avatar_url(char_id):
        # 使用 Aceship 的 GitHub 资源库，需要标准 char_id (如 char_102_texas)
        # 如果你的 id 是纯数字或其他格式，这里可能需要调整，或者使用 prts.wiki
        return f"https://raw.githubusercontent.com/Aceship/Arknight-Images/main/avatars/{char_id}.png"

    # --- 辅助函数：数据去重与排序（修复版 + 配合本地图库） ---
    def process_suggestions(suggestions):
        seen = set()
        unique_list = []

        # 安全排序
        sorted_sugg = sorted(suggestions, key=lambda x: x.get('gain', 0), reverse=True)

        for item in sorted_sugg:
            try:
                # 补全 ID 信息 (非常重要的一步)
                if item.get('type') == 'bundle':
                    for op in item.get('ops', []):
                        if not op.get('id'):
                            op['id'] = get_real_id(op)
                else:
                    if not item.get('id'):
                        item['id'] = get_real_id(item)

                # 生成唯一标识符
                if item.get('type') == 'bundle':
                    ops = item.get('ops', [])
                    # 使用 get_real_id 确保万无一失
                    ids = [str(o.get('id') or o.get('name')) for o in ops]
                    uid = "bundle_" + "_".join(sorted(ids))
                else:
                    ident = item.get('id') or item.get('name')
                    uid = f"single_{ident}"

                if uid not in seen:
                    seen.add(uid)
                    unique_list.append(item)
            except Exception:
                continue

        return unique_list


    # 处理数据
    if not st.session_state.suggestions:
        st.info("✨ 当前练度已满足该配置的理论最优解，无需额外提升。")
        processed_suggestions = []
    else:
        processed_suggestions = process_suggestions(st.session_state.suggestions)
        st.write(f"检测到 **{len(processed_suggestions)}** 项可提升效率的优化点：")

    # --- 样式优化 ---
    st.markdown("""
    <style>
    .op-card {
        background-color: #262730; /* 适配暗色模式，如果是亮色模式需改为 #f0f2f6 */
        border: 1px solid #464b59;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    .eff-badge {
        background-color: rgba(255, 75, 75, 0.2);
        color: #ff4b4b;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.9em;
        white-space: nowrap;
    }
    .eff-badge-high {
        background-color: rgba(255, 215, 0, 0.2);
        color: #ffd700;
    }
    .op-name {
        font-weight: bold;
        font-size: 1.1em;
        margin-left: 10px;
    }
    .op-desc {
        font-size: 0.85em;
        color: #a0a0a0;
        margin-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 表单区域 ---
    with st.form("upgrade_form"):
        # 全选控制逻辑
        # 使用 session_state 来控制全选状态稍微复杂，这里用简单的列头Checkbox作为全选不太容易实现联动
        # 替代方案：默认全部勾选，或者提供两个按钮在表单外控制（Streamlit限制）
        # 这里采用：顶部加一个说明，默认不勾选，或者用户手动勾选。
        # 为了体验，通常建议**默认全选**或提供**全选按钮**。
        # 由于Streamlit Form机制，我们在Form内部很难做动态的全选/反选交互。
        # 折中方案：默认全部 False，用户自己勾。

        # Grid 布局
        cols = st.columns(1)  # 手机端友好，单列布局

        selected_indices_in_processed = []

        # 遍历渲染列表
        for idx, item in enumerate(processed_suggestions):
            # 获取数据
            gain_val = item['gain']
            is_bundle = item.get('type') == 'bundle'

            # 准备显示的 HTML 内容
            if is_bundle:
                # 组合建议
                ops_info = item['ops']
                avatars_html = ""
                names_text = []
                details_text = []
                ids_for_key = []

                for o in ops_info:
                    # [修改] 使用本地 Base64 读取
                    real_id = o.get('id')  # 在 process_suggestions 里已经补全了
                    img_src = get_avatar_base64(real_id)

                    if img_src:
                        avatars_html += f'<img src="{img_src}" style="width: 40px; height: 40px; border-radius: 4px; margin-right: 5px; object-fit: cover;">'
                    else:
                        # 图片缺失时的文字占位
                        avatars_html += f'<span style="display:inline-block; width:40px; text-align:center; font-size:10px; color:#aaa; border:1px solid #555; border-radius:4px; margin-right:5px;">{o["name"][:1]}</span>'

                    names_text.append(o['name'])
                    details_text.append(f"{o['name']}: 精{o['current']}→{o['target']}")
                    ids_for_key.append(str(real_id))

                display_name = " + ".join(names_text)
                desc_text = " | ".join(details_text)
                key_suffix = "_".join(ids_for_key)
            else:
                # 单人建议
                real_id = item.get('id')
                img_src = get_avatar_base64(real_id)

                if img_src:
                    avatars_html = f'<img src="{img_src}" style="width: 45px; height: 45px; border-radius: 4px; object-fit: cover;">'
                else:
                    avatars_html = f'<div style="width:45px; height:45px; background:#333; border-radius:4px; display:flex; align-items:center; justify-content:center; color:#aaa;">{item["name"][:1]}</div>'

                display_name = item['name']
                desc_text = f"当前: 精{item['current']}  ➜  目标: 精{item['target']}"
                key_suffix = str(real_id)

            # 效率颜色区分：超过 20% 显示金色，否则红色
            badge_class = "eff-badge eff-badge-high" if gain_val >= 20 else "eff-badge"

            # 使用 container 模拟卡片
            # 注意：在 Form 里无法使用复杂的嵌套 columns 布局而不破坏 checkbox 对齐
            # 这里的方案是：Checkbox 在左，右侧使用 HTML 渲染详情

            c1, c2 = st.columns([0.1, 0.9])
            with c1:
                # 垂直居中稍微难一点，这里简单处理
                st.write("")
                st.write("")
                # 唯一的 Key，结合版本号防止状态混淆
                unique_key = f"chk_{st.session_state.list_version}_{idx}_{key_suffix}"
                is_checked = st.checkbox("选择", key=unique_key, label_visibility="collapsed")
                if is_checked:
                    selected_indices_in_processed.append(idx)

            with c2:
                st.markdown(f"""
                <div class="op-card">
                    <div style="display:flex; align-items:center; flex-grow:1;">
                        {avatars_html}
                        <div style="display:flex; flex-direction:column;">
                            <span class="op-name">{display_name}</span>
                            <span class="op-desc">{desc_text}</span>
                        </div>
                    </div>
                    <div class="{badge_class}">
                        +{gain_val:.2f}% 效率
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # 操作按钮
        c_btn1, c_btn2 = st.columns([3, 1])
        with c_btn1:
            submit_btn = st.form_submit_button("🚀 应用选中修改并生成排班", type="primary", use_container_width=True)
        with c_btn2:
            st.caption(f"已选中: {len(selected_indices_in_processed)} 项")

    # ==========================================
    # 4. 处理生成逻辑 (适配新的去重列表)
    # ==========================================
    if submit_btn:
        with st.spinner("正在写入数据并重新演算..."):
            # A. 复制当前数据
            new_ops_data = copy.deepcopy(st.session_state.user_ops)
            modified_names = []

            # B. 应用勾选的修改 (注意：这里要用 processed_suggestions)
            for idx in selected_indices_in_processed:
                item = processed_suggestions[idx]  # <--- 使用去重后的列表

                if item.get('type') == 'bundle':
                    for o in item['ops']:
                        suc, name = upgrade_operator_in_memory(new_ops_data, o.get('id'), o.get('name'),
                                                               o['target'])
                        if suc: modified_names.append(name)
                else:
                    suc, name = upgrade_operator_in_memory(new_ops_data, item.get('id'), item.get('name'),
                                                           item['target'])
                    if suc: modified_names.append(name)

            # ... (后续代码保持不变，直到 st.rerun()) ...

            # --- 以下代码直接接你原有的 C, D, E 步骤 ---
            # C. 保存到硬盘
            if modified_names:
                save_success = save_user_data(st.session_state.user_hash, new_ops_data)
                if not save_success:
                    st.error("保存数据失败，请联系管理员")
                    st.stop()
                st.session_state.user_ops = new_ops_data

            # D. 生成最终排班
            run_ops_path = f"run_ops_{st.session_state.user_hash}.json"
            run_conf_path = f"run_conf_{st.session_state.user_hash}.json"

            try:
                with open(run_ops_path, "w", encoding='utf-8') as f:
                    json.dump(new_ops_data, f, ensure_ascii=False)
                with open(run_conf_path, "w", encoding='utf-8') as f:
                    json.dump(st.session_state.user_conf, f, ensure_ascii=False)

                optimizer = WorkplaceOptimizer("internal", run_ops_path, run_conf_path)
                final_res = optimizer.get_optimal_assignments(ignore_elite=False)

                raw_res = final_res.get('raw_results', [])
                st.session_state.final_eff = raw_res[0].total_efficiency if raw_res else 0
                st.session_state.final_result_json = json.dumps(clean_data(final_res), ensure_ascii=False, indent=2)

                st.session_state.final_result_ready = True
                st.session_state.analysis_done = False
                st.session_state.suggestions = []

                if modified_names:
                    st.session_state.list_version += 1

                if modified_names:
                    st.toast(f"✅ 已更新 {len(modified_names)} 位干员练度！", icon="💾")
                else:
                    st.toast("✅ 排班生成成功！", icon="📄")

                time.sleep(0.5)
                st.rerun()

            except Exception as e:
                st.error(f"计算发生错误: {e}")
            finally:
                if os.path.exists(run_ops_path): os.remove(run_ops_path)
                if os.path.exists(run_conf_path): os.remove(run_conf_path)