"""数据库种子脚本：扬州非遗演示数据。

数据说明：
- 14 个非遗项目、16 位传承人、5 个关卡、50 道题目，与前端 Mock 数据
  （mobile-app/api/mock/data.js）及 database/mysql/seed.sql 一致；
- 项目/传承人/关卡/题目均显式指定主键 ID，保证与知识图谱演示数据
  （graph_service）及前端节点 ID（h1 / i101 / c1...）对齐；
- 另含 6 个演示用户（1 个管理员 + 5 个排行榜用户），便于演示积分排行榜。

使用方式：
- 启动 main.py 时若数据库为空自动调用（try 包裹，失败仅告警不阻断）；
- 也可手动执行：python -m scripts.seed_data
"""
from __future__ import annotations

import logging

from app.core.database import Base, SessionLocal, engine
from app.models.game import GameLevel, GameQuestion
from app.models.heritage import HeritageProject, Inheritor
from app.models.user import SysUser

logger = logging.getLogger("heritouch.seed")

# 识图题占位图（SVG 矢量占位，无需二进制素材；见 server/static/images/questions/）
QUIZ_IMAGE_PREFIX = "/static/images/questions"
# 传承人头像占位
AVATAR_PLACEHOLDER = "/static/images/avatar-placeholder.svg"

# =====================================================================
# 一、非遗项目（14 个，id 1-14）
# =====================================================================
PROJECTS: list[dict] = [
    {
        "id": 1,
        "name": "扬州剪纸",
        "level": "国家级",
        "category": "传统美术",
        "region": "江苏扬州",
        "batch": 2006,
        "intro": "扬州剪纸是南方剪纸艺术的代表流派之一，以“细、秀、雅、活”著称，题材涵盖花鸟虫鱼、戏曲人物与民俗生活，尤以“剪纸绣样”最具特色。",
        "history": "扬州剪纸源于唐宋，兴盛于明清。清代扬州盐商云集，民俗活动兴盛，剪纸广泛应用于刺绣样稿、喜庆装饰与灯彩制作，逐渐形成秀美灵动的艺术风格。",
        "craft": "选纸→起稿→剪刻→点染。艺人以宣纸或彩纸为料，运以尖口小剪，线条细如发丝；点色剪纸采用“一手剪、一手染”技法，色彩晕染自然。",
        "cover_image": "/static/images/projects/paper-cut.svg",
        "audio_mandarin": "/static/audio/jianzhi-mandarin.mp3",
        "audio_dialect": "/static/audio/jianzhi-dialect.mp3",
        "qrcode": "/static/images/qrcode-1.png",
        "latitude": 32.394,
        "longitude": 119.412,
    },
    {
        "id": 2,
        "name": "扬州玉雕",
        "level": "国家级",
        "category": "传统美术",
        "region": "江苏扬州",
        "batch": 2006,
        "intro": "扬州玉雕以“浑厚、圆润、儒雅、灵秀”见长，讲究“因料施艺、量材取形”，尤其擅长大型山子雕，被誉为中国玉雕的“南派”代表。",
        "history": "扬州琢玉工艺可追溯至四千年前的江淮新石器时代；两汉、隋唐持续发展，明清因盐商经济推动达到鼎盛，“扬州工”名扬天下。",
        "craft": "相玉→设计→琢碾→细作→抛光。先审石度色、因形就势，再以铡、錾、冲、轧等技法层层推进，最后精细打磨显玉质温润。",
        "cover_image": "/static/images/projects/jade-carving.svg",
        "audio_mandarin": "/static/audio/yudiao-mandarin.mp3",
        "audio_dialect": "/static/audio/yudiao-dialect.mp3",
        "qrcode": "/static/images/qrcode-2.png",
        "latitude": 32.391,
        "longitude": 119.421,
    },
    {
        "id": 3,
        "name": "扬州漆器髹饰技艺",
        "level": "国家级",
        "category": "传统技艺",
        "region": "江苏扬州",
        "batch": 2006,
        "intro": "扬州漆器造型古朴典雅，工艺精湛繁复，综合运用雕漆、点螺、平磨螺钿等“十大工艺”，是中国漆器艺术的高峰。",
        "history": "扬州漆器起源于战国，汉代广陵漆器已负盛名；唐代“金银平脱”、宋代“雕红漆”、明清雕漆嵌玉鼎盛，清代为宫廷御用贡品。",
        "craft": "制胎→髹漆→打磨→装饰。一件雕漆作品需髹涂数十至数百道漆，每道须在窨房中阴干，再行刀刻，耗时可达数年。",
        "cover_image": "/static/images/projects/lacquerware.svg",
        "audio_mandarin": "/static/audio/qiqi-mandarin.mp3",
        "audio_dialect": "/static/audio/qiqi-dialect.mp3",
        "qrcode": "/static/images/qrcode-3.png",
        "latitude": 32.398,
        "longitude": 119.435,
    },
    {
        "id": 4,
        "name": "扬州评话",
        "level": "国家级",
        "category": "曲艺",
        "region": "江苏扬州",
        "batch": 2006,
        "intro": "扬州评话以扬州方言说表，讲究“口、手、眼、身、步”五功，长篇书目众多，是扬州书场的代表性曲种。",
        "history": "扬州评话形成于明末清初，与扬州运河商业繁荣、书场文化兴盛密切相关，清乾隆年间达到高峰，名家辈出。",
        "craft": "坐唱→说表→演口→噱功。演员一人摹拟百样角色，以折扇、醒木为道具，方口与圆口结合，叙事中夹评夹议。",
        "cover_image": "/static/images/projects/pinghua.svg",
        "audio_mandarin": "/static/audio/pinghua-mandarin.mp3",
        "audio_dialect": "/static/audio/pinghua-dialect.mp3",
        "qrcode": "/static/images/qrcode-4.png",
        "latitude": 32.402,
        "longitude": 119.418,
    },
    {
        "id": 5,
        "name": "扬剧",
        "level": "国家级",
        "category": "传统戏剧",
        "region": "江苏扬州",
        "batch": 2006,
        "intro": "扬剧由扬州花鼓戏、香火戏与扬州清曲融合发展而成，唱腔清新华丽、生活气息浓郁，是江苏代表性地方戏曲剧种之一。",
        "history": "扬剧发端于清代扬州民间花鼓与香火会戏，民国年间进入上海演出后定名“扬剧”，逐渐形成完整的行当与唱腔体系。",
        "craft": "唱→念→做→打。以“大开口”“小开口”为基础唱腔，兼收民歌小调，表演文武兼备、诙谐生动。",
        "cover_image": "/static/images/projects/yangju.svg",
        "audio_mandarin": "/static/audio/yangju-mandarin.mp3",
        "audio_dialect": "/static/audio/yangju-dialect.mp3",
        "qrcode": "/static/images/qrcode-5.png",
        "latitude": 32.405,
        "longitude": 119.424,
    },
    {
        "id": 6,
        "name": "扬州清曲",
        "level": "国家级",
        "category": "曲艺",
        "region": "江苏扬州",
        "batch": 2006,
        "intro": "扬州清曲又称“扬州小曲”或“广陵清曲”，以坐唱形式演出，曲牌丰富、唱腔婉转，被誉为“里下河音乐的活化石”。",
        "history": "扬州清曲源于元代小唱，明清时期吸收各地小曲在扬州融汇定型，清末民初最为流行，后成为扬剧的重要唱腔来源。",
        "craft": "坐唱→夹白→帮腔。乐队以琵琶、三弦、二胡、酒杯与瓷碟为器，击碟声清越，曲牌连缀叙事。",
        "cover_image": "/static/images/projects/qingqu.svg",
        "audio_mandarin": "/static/audio/qingqu-mandarin.mp3",
        "audio_dialect": "/static/audio/qingqu-dialect.mp3",
        "qrcode": "/static/images/qrcode-6.png",
        "latitude": 32.399,
        "longitude": 119.409,
    },
    {
        "id": 7,
        "name": "古琴艺术（广陵琴派）",
        "level": "国家级",
        "category": "传统音乐",
        "region": "江苏扬州",
        "batch": 2008,
        "intro": "广陵琴派是中国古琴最具影响力的流派之一，风格“跌宕多变、刚柔相济”，指法细腻，代表曲目多与扬州文化意象相关。",
        "history": "广陵琴派形成于清代扬州，以徐常遇为代表开创，经秦维瀚《蕉庵琴谱》系统化，近现代张子谦、刘少椿等名家薪火相传。",
        "craft": "识谱→指法→吟猱→会意。演奏讲究“重弦轻捻”，以吟猱绰注表现山水意境，琴曲多寄情江南风月。",
        "cover_image": "/static/images/projects/guqin.svg",
        "audio_mandarin": "/static/audio/guqin-mandarin.mp3",
        "audio_dialect": "/static/audio/guqin-dialect.mp3",
        "qrcode": "/static/images/qrcode-7.png",
        "latitude": 32.396,
        "longitude": 119.445,
    },
    {
        "id": 8,
        "name": "扬州刺绣",
        "level": "省级",
        "category": "传统美术",
        "region": "江苏扬州",
        "batch": 2007,
        "intro": "扬州刺绣以“仿古绣”与“水墨绣”著称，针法多变、绣理细腻，善于表现书画笔墨的浓淡干湿，有“针画”之誉。",
        "history": "扬州刺绣自汉代发端，宋代已有专业化绣坊，清代与扬州画派互动密切，形成以绣仿画、画绣结合的地方特色。",
        "craft": "设计→上绷→配线→刺绣→装裱。以针代笔、以线代墨，一件仿古绣作品需运用数十种针法层层晕染。",
        "cover_image": "/static/images/projects/embroidery.svg",
        "audio_mandarin": "/static/audio/cixiu-mandarin.mp3",
        "audio_dialect": "/static/audio/cixiu-dialect.mp3",
        "qrcode": "/static/images/qrcode-8.png",
        "latitude": 32.388,
        "longitude": 119.428,
    },
    {
        "id": 9,
        "name": "蓝印花布印染技艺",
        "level": "省级",
        "category": "传统技艺",
        "region": "江苏扬州",
        "batch": 2007,
        "intro": "扬州蓝印花布以天然蓝草发酵染色，图案朴素典雅，蓝白相映，广泛用于被面、帐檐、服饰与民俗用品。",
        "history": "蓝印花布在江淮地区流传久远，清代扬州为重要产销地，染坊林立，“扬州蓝”与“南通蓝”并称江苏蓝印花布两大系统。",
        "craft": "刻版→刮浆→浸染→刮灰→漂洗。以黄豆粉加石灰防染，靛缸低温多次浸染，蓝度逐日加深。",
        "cover_image": "/static/images/projects/blue-calico.svg",
        "audio_mandarin": "/static/audio/lanyin-mandarin.mp3",
        "audio_dialect": "/static/audio/lanyin-dialect.mp3",
        "qrcode": "/static/images/qrcode-9.png",
        "latitude": 32.407,
        "longitude": 119.401,
    },
    {
        "id": 10,
        "name": "富春茶点制作技艺",
        "level": "国家级",
        "category": "传统技艺",
        "region": "江苏扬州",
        "batch": 2008,
        "intro": "富春茶点以“魁龙珠”茶与三丁包、翡翠烧卖等细点闻名，讲究“茶以点心佐、点以茶兴味”，是扬州早茶文化的代表。",
        "history": "富春茶社创于清代光绪年间，百年间形成“花、茶、点、菜”结合的淮扬茶食体系，“早上皮包水”的扬州生活习俗由此传扬。",
        "craft": "和面→制馅→包捏→醒发→蒸制。三丁包讲究“鸡丁大、笋丁脆、肉丁香”，擀皮要求“底厚边薄”十八道褶。",
        "cover_image": "/static/images/projects/fuchun-tea.svg",
        "audio_mandarin": "/static/audio/fuchun-mandarin.mp3",
        "audio_dialect": "/static/audio/fuchun-dialect.mp3",
        "qrcode": "/static/images/qrcode-10.png",
        "latitude": 32.393,
        "longitude": 119.416,
    },
    {
        "id": 11,
        "name": "杖头木偶戏（扬州杖头木偶）",
        "level": "省级",
        "category": "传统戏剧",
        "region": "江苏扬州",
        "batch": 2007,
        "intro": "扬州杖头木偶以“内扦”结构为特色，木偶可眼珠转动、口唇开合，表演细腻传神，尤擅武戏与特技。",
        "history": "扬州木偶戏起源于清代泰兴、兴化一带的“傀儡戏”，20世纪50年代扬州市木偶剧团成立后艺术体系日趋完备。",
        "craft": "举→转→捻→勾。演员以三根扦子操控木偶头、双手，配合身段步法，做到“人偶合一”。",
        "cover_image": "/static/images/projects/puppet.svg",
        "audio_mandarin": "/static/audio/muou-mandarin.mp3",
        "audio_dialect": "/static/audio/muou-dialect.mp3",
        "qrcode": "/static/images/qrcode-11.png",
        "latitude": 32.412,
        "longitude": 119.43,
    },
    {
        "id": 12,
        "name": "高邮民歌",
        "level": "省级",
        "category": "传统音乐",
        "region": "江苏扬州（高邮）",
        "batch": 2007,
        "intro": "高邮民歌里下河风格浓郁，号子、小调、情歌并存，《数鸭蛋》《撒趟子撂在外》等曲目流传甚广。",
        "history": "高邮地处里下河水网地带，秧歌、车水号子、渔歌在劳作中世代传唱，20世纪50年代起经系统采集整理登上全国舞台。",
        "craft": "领唱→和腔→对歌。一唱众和、即兴填词，曲调随水乡劳作节奏起伏。",
        "cover_image": "/static/images/projects/gaoyou-folk.svg",
        "audio_mandarin": "/static/audio/gaoyou-mandarin.mp3",
        "audio_dialect": "/static/audio/gaoyou-dialect.mp3",
        "qrcode": "/static/images/qrcode-12.png",
        "latitude": 32.784,
        "longitude": 119.459,
    },
    {
        "id": 13,
        "name": "扬州“三把刀”技艺",
        "level": "省级",
        "category": "民俗",
        "region": "江苏扬州",
        "batch": 2007,
        "intro": "“扬州三把刀”指厨刀、修脚刀、剃头刀，集中体现扬州生活技艺的精巧，是扬州澡堂文化与早茶习俗的活态载体。",
        "history": "清代扬州盐商奢靡之风带动服务业兴盛，“上午皮包水、下午水包皮”的习俗孕育出精湛的厨艺与修脚、理发技艺。",
        "craft": "厨刀→淮扬菜刀工；修脚刀→斫、断、劈、片；剃头刀→剃、修、推、捏。",
        "cover_image": "/static/images/projects/three-knives.svg",
        "audio_mandarin": "/static/audio/sandao-mandarin.mp3",
        "audio_dialect": "/static/audio/sandao-dialect.mp3",
        "qrcode": "/static/images/qrcode-13.png",
        "latitude": 32.389,
        "longitude": 119.404,
    },
    {
        "id": 14,
        "name": "夏氏内科疗法（扬州中医）",
        "level": "省级",
        "category": "传统医药",
        "region": "江苏扬州",
        "batch": 2016,
        "intro": "夏氏内科以“轻可去实”的用药风格著称，擅长外感热病与脾胃病诊治，为扬州中医世家医术的代表。",
        "history": "夏氏内科发端于清末扬州中医世家，历经数代传承，形成以“简、便、验、廉”为特色的诊疗经验体系。",
        "craft": "四诊合参→辨证立法→遣方用药。强调因地因人制宜，药味精简、轻清灵动。",
        "cover_image": "/static/images/projects/tcm.svg",
        "audio_mandarin": "/static/audio/tcm-mandarin.mp3",
        "audio_dialect": "/static/audio/tcm-dialect.mp3",
        "qrcode": "/static/images/qrcode-14.png",
        "latitude": 32.401,
        "longitude": 119.437,
    },
]

# =====================================================================
# 二、传承人（16 位，id 101-116，与知识图谱 inheritor 节点对齐）
# =====================================================================
INHERITORS: list[dict] = [
    {
        "id": 101,
        "name": "张秀芳",
        "gender": "女",
        "project_name": "扬州剪纸",
        "title": "国家级代表性传承人",
        "biography": "扬州剪纸代表性传承人，以点色剪纸见长，作品构图精巧、线条流畅，长期致力于剪纸进校园传承活动。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 102,
        "name": "熊崇荣",
        "gender": "男",
        "project_name": "扬州剪纸",
        "title": "市级代表性传承人",
        "biography": "从事剪纸创作四十余年，擅长民俗题材大幅剪纸创作，多次在各类非遗展演中现场献艺。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 103,
        "name": "江春",
        "gender": "男",
        "project_name": "扬州玉雕",
        "title": "国家级代表性传承人",
        "biography": "扬州玉雕名家，精于山子雕与人物件，主张“因料施艺”，作品多次获中国工艺美术百花奖。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 104,
        "name": "张来喜",
        "gender": "男",
        "project_name": "扬州漆器髹饰技艺",
        "title": "国家级代表性传承人",
        "biography": "扬州漆器雕漆工艺代表性传承人，掌握雕漆嵌玉核心技艺，作品气势恢宏、刀法深峻。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 105,
        "name": "池家骏",
        "gender": "男",
        "project_name": "扬州漆器髹饰技艺",
        "title": "市级代表性传承人",
        "biography": "扬州漆器点螺工艺传承人，专注传统髹饰技艺的恢复与创新，尤擅点螺屏风制作。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 106,
        "name": "王丽堂",
        "gender": "女",
        "project_name": "扬州评话",
        "title": "国家级代表性传承人",
        "biography": "扬州评话名家，以《水浒》系列书目享誉书坛，说口清脆、形神兼备，被誉为“武水浒”的代表。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 107,
        "name": "李开敏",
        "gender": "女",
        "project_name": "扬剧",
        "title": "省级代表性传承人",
        "biography": "扬剧表演艺术家，唱腔婉转清丽，代表作《百岁挂帅》《恩仇记》，致力于扬剧青年演员培养。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 108,
        "name": "聂峰",
        "gender": "男",
        "project_name": "扬州清曲",
        "title": "省级代表性传承人",
        "biography": "扬州清曲演唱与研究专家，整理大量传统曲牌，推动清曲进校园与数字化传播。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 109,
        "name": "马维衡",
        "gender": "男",
        "project_name": "古琴艺术（广陵琴派）",
        "title": "省级代表性传承人",
        "biography": "广陵琴派琴家，擅弹《平沙落雁》《山居吟》，致力于古琴制作技艺研究与琴学传承。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 110,
        "name": "卫芳",
        "gender": "女",
        "project_name": "扬州刺绣",
        "title": "市级代表性传承人",
        "biography": "扬州刺绣传承人，专攻仿古山水绣与水墨绣，作品以针法细腻、绣理自然见长。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 111,
        "name": "王稳扬",
        "gender": "男",
        "project_name": "蓝印花布印染技艺",
        "title": "市级代表性传承人",
        "biography": "蓝印花布印染技艺传承人，坚持古法靛蓝发酵与手工刮浆，产品远销海内外。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 112,
        "name": "徐永珍",
        "gender": "女",
        "project_name": "富春茶点制作技艺",
        "title": "国家级代表性传承人",
        "biography": "富春茶点制作技艺代表性传承人，精通包子、烧卖等淮扬细点制作，被誉为“点心状元”。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 113,
        "name": "封春来",
        "gender": "男",
        "project_name": "杖头木偶戏（扬州杖头木偶）",
        "title": "市级代表性传承人",
        "biography": "扬州杖头木偶操控技艺传承人，擅长武戏与木偶特技表演，多次随团出国演出。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 114,
        "name": "王兰英",
        "gender": "女",
        "project_name": "高邮民歌",
        "title": "省级代表性传承人",
        "biography": "高邮民歌演唱家，嗓音高亢嘹亮，擅长秧歌号子与情歌对唱，积极辅导乡村民歌手。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 115,
        "name": "陆琴",
        "gender": "女",
        "project_name": "扬州“三把刀”技艺",
        "title": "市级代表性传承人",
        "biography": "扬州修脚技艺代表性传承人，创立“陆氏修脚术”，以“稳、轻、准”著称。",
        "photo": AVATAR_PLACEHOLDER,
    },
    {
        "id": 116,
        "name": "夏雨生",
        "gender": "男",
        "project_name": "夏氏内科疗法（扬州中医）",
        "title": "市级代表性传承人",
        "biography": "夏氏内科传人，临床擅用轻清灵动之剂调理脾胃与外感热病。",
        "photo": AVATAR_PLACEHOLDER,
    },
]

# =====================================================================
# 三、闯关关卡（5 个）
# =====================================================================
LEVELS: list[dict] = [
    {
        "id": 1,
        "name": "入门学徒",
        "subtitle": "初识扬州非遗",
        "rank": "学徒",
        "need_score": 0,
        "theme": "基础认知",
        "question_count": 10,
        "icon": "🌱",
        "sort": 1,
    },
    {
        "id": 2,
        "name": "匠人弟子",
        "subtitle": "技艺门类辨一辨",
        "rank": "弟子",
        "need_score": 100,
        "theme": "传统技艺",
        "question_count": 10,
        "icon": "🔨",
        "sort": 2,
    },
    {
        "id": 3,
        "name": "曲苑知音",
        "subtitle": "戏曲曲艺听门道",
        "rank": "弟子",
        "need_score": 250,
        "theme": "戏剧曲艺",
        "question_count": 10,
        "icon": "🎭",
        "sort": 3,
    },
    {
        "id": 4,
        "name": "丹青圣手",
        "subtitle": "美术与图案的世界",
        "rank": "匠人",
        "need_score": 450,
        "theme": "传统美术",
        "question_count": 10,
        "icon": "🖌️",
        "sort": 4,
    },
    {
        "id": 5,
        "name": "非遗大师",
        "subtitle": "综合大闯关",
        "rank": "大师",
        "need_score": 700,
        "theme": "综合进阶",
        "question_count": 10,
        "icon": "🏆",
        "sort": 5,
    },
]

# =====================================================================
# 四、题库（50 道：single 单选 / judge 判断 / image 识图，分布 level 1-5）
# =====================================================================
QUESTIONS: list[dict] = [
    # ---------- 第一关：入门学徒 ----------
    {"id": 1, "level_id": 1, "question_type": "single", "question_text": "扬州剪纸属于下列哪一类非遗？", "option_a": "传统美术", "option_b": "传统戏剧", "option_c": "传统医药", "option_d": "民俗", "answer": "A", "analysis": "扬州剪纸是国家级传统美术类非遗，以细秀雅活著称。", "image": None, "difficulty": 1},
    {"id": 2, "level_id": 1, "question_type": "judge", "question_text": "扬州玉雕以大型山子雕见长，被誉为中国玉雕“南派”代表。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "扬州玉雕讲究因料施艺，山子雕是其标志性品类。", "image": None, "difficulty": 1},
    {"id": 3, "level_id": 1, "question_type": "single", "question_text": "“早上皮包水、下午水包皮”描述的是扬州哪种生活习俗？", "option_a": "早茶与澡堂文化", "option_b": "庙会与集市", "option_c": "农耕与渔猎", "option_d": "书院与科举", "answer": "A", "analysis": "该俗语对应扬州早茶与澡堂文化，是“三把刀”技艺的生活土壤。", "image": None, "difficulty": 1},
    {"id": 4, "level_id": 1, "question_type": "single", "question_text": "富春茶点制作技艺中最具代表性的茶叶是？", "option_a": "魁龙珠", "option_b": "铁观音", "option_c": "普洱", "option_d": "大红袍", "answer": "A", "analysis": "魁龙珠由龙井、魁针、珠兰窨制而成，是富春茶社的代表茶。", "image": None, "difficulty": 1},
    {"id": 5, "level_id": 1, "question_type": "judge", "question_text": "扬剧是由扬州花鼓戏、香火戏与扬州清曲融合发展而成的地方戏曲。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "扬剧融合花鼓戏、香火戏与清曲，是江苏代表性剧种。", "image": None, "difficulty": 1},
    {"id": 6, "level_id": 1, "question_type": "single", "question_text": "下列哪一项是扬州漆器的标志性工艺？", "option_a": "雕漆嵌玉", "option_b": "景泰蓝掐丝", "option_c": "景德镇青花", "option_d": "龙泉哥窑", "answer": "A", "analysis": "扬州漆器综合雕漆、点螺、平磨螺钿等工艺，雕漆嵌玉最具特色。", "image": None, "difficulty": 1},
    {"id": 7, "level_id": 1, "question_type": "image", "question_text": "下图所示为哪种扬州非遗技艺的作品？", "option_a": "漆器髹饰", "option_b": "蓝印花布", "option_c": "剪纸", "option_d": "玉雕", "answer": "A", "analysis": "图中作品为雕漆嵌玉风格，是扬州漆器的典型样式。", "image": f"{QUIZ_IMAGE_PREFIX}/quiz-lacquer.svg", "difficulty": 1},
    {"id": 8, "level_id": 1, "question_type": "single", "question_text": "扬州评话表演时使用的道具组合是？", "option_a": "折扇与醒木", "option_b": "三弦与鼓板", "option_c": "二胡与琵琶", "option_d": "锣鼓与唢呐", "answer": "A", "analysis": "扬州评话以折扇、醒木为道具，讲究口手眼身步五功。", "image": None, "difficulty": 1},
    {"id": 9, "level_id": 1, "question_type": "judge", "question_text": "高邮民歌是流传于扬州里下河水乡的民歌系统。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "高邮民歌为江苏省级非遗，里下河风格浓郁。", "image": None, "difficulty": 1},
    {"id": 10, "level_id": 1, "question_type": "single", "question_text": "扬州刺绣最负盛名的品类是？", "option_a": "仿古绣", "option_b": "苏绣双面绣", "option_c": "湘绣狮虎", "option_d": "粤绣金线", "answer": "A", "analysis": "扬州刺绣以仿古绣和水墨绣著称，善于表现书画笔墨意趣。", "image": None, "difficulty": 1},
    # ---------- 第二关：匠人弟子 ----------
    {"id": 11, "level_id": 2, "question_type": "single", "question_text": "蓝印花布印染中起防染作用的材料是？", "option_a": "黄豆粉加石灰", "option_b": "蜂蜡", "option_c": "松香", "option_d": "面粉糊", "answer": "A", "analysis": "黄豆粉加石灰刮浆形成防染层，靛缸浸染后呈蓝白花纹。", "image": None, "difficulty": 2},
    {"id": 12, "level_id": 2, "question_type": "judge", "question_text": "一件雕漆作品往往需要髹涂数十至数百道大漆。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "雕漆需层层髹涂、道道阴干，耗时可达数年。", "image": None, "difficulty": 2},
    {"id": 13, "level_id": 2, "question_type": "single", "question_text": "富春三丁包的“三丁”不包括下列哪一项？", "option_a": "笋丁", "option_b": "鸡丁", "option_c": "肉丁", "option_d": "虾丁", "answer": "D", "analysis": "三丁指鸡丁、肉丁、笋丁，讲究鸡丁大、笋丁脆、肉丁香。", "image": None, "difficulty": 2},
    {"id": 14, "level_id": 2, "question_type": "single", "question_text": "广陵琴派是中国古琴的重要流派，其艺术风格被概括为？", "option_a": "跌宕多变、刚柔相济", "option_b": "苍古雄健", "option_c": "细腻婉约如吴语", "option_d": "高亢激越", "answer": "A", "analysis": "广陵琴派风格跌宕多变、刚柔相济，指法细腻。", "image": None, "difficulty": 2},
    {"id": 15, "level_id": 2, "question_type": "single", "question_text": "扬州“三把刀”指的是？", "option_a": "厨刀、修脚刀、剃头刀", "option_b": "菜刀、剪刀、镰刀", "option_c": "刻刀、剪刀、裁纸刀", "option_d": "厨刀、剪刀、修脚刀", "answer": "A", "analysis": "三把刀集中体现扬州生活服务业技艺的精巧。", "image": None, "difficulty": 2},
    {"id": 16, "level_id": 2, "question_type": "image", "question_text": "下图所示为哪种非遗的典型图案？", "option_a": "蓝印花布", "option_b": "玉雕", "option_c": "漆器", "option_d": "木偶", "answer": "A", "analysis": "图中为蓝印花布经典图案，蓝白相映。", "image": f"{QUIZ_IMAGE_PREFIX}/quiz-calico.svg", "difficulty": 2},
    {"id": 17, "level_id": 2, "question_type": "judge", "question_text": "扬州剪纸的“点色剪纸”采用“一手剪、一手染”技法。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "点色剪纸染色自然灵动，是扬州剪纸特色技法。", "image": None, "difficulty": 2},
    {"id": 18, "level_id": 2, "question_type": "single", "question_text": "扬州杖头木偶的结构特点是？", "option_a": "内扦", "option_b": "外扦", "option_c": "提线", "option_d": "布袋", "answer": "A", "analysis": "扬州杖头木偶以内扦结构为特色，可眼转口开。", "image": None, "difficulty": 2},
    {"id": 19, "level_id": 2, "question_type": "single", "question_text": "下列哪种材料不是扬州漆器髹饰的常用材料？", "option_a": "景德镇瓷土", "option_b": "大漆", "option_c": "螺钿", "option_d": "金银箔", "answer": "A", "analysis": "漆器以大漆、螺钿、金银箔等为材，与瓷土无关。", "image": None, "difficulty": 2},
    {"id": 20, "level_id": 2, "question_type": "judge", "question_text": "扬州玉雕讲究“因料施艺、量材取形”。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "因料施艺是扬州玉雕的核心创作原则。", "image": None, "difficulty": 2},
    # ---------- 第三关：曲苑知音 ----------
    {"id": 21, "level_id": 3, "question_type": "single", "question_text": "扬州评话说表时讲究“五功”，指的是？", "option_a": "口、手、眼、身、步", "option_b": "说、学、逗、唱、演", "option_c": "唱、念、做、打、翻", "option_d": "吹、拉、弹、打、舞", "answer": "A", "analysis": "扬州评话五功为口手眼身步。", "image": None, "difficulty": 2},
    {"id": 22, "level_id": 3, "question_type": "single", "question_text": "扬剧的两大基础唱腔系统是？", "option_a": "大开口与小开口", "option_b": "皮黄与梆子", "option_c": "高腔与昆腔", "option_d": "评弹与宣卷", "answer": "A", "analysis": "扬剧唱腔以“大开口”“小开口”为基础，兼收民歌小调。", "image": None, "difficulty": 2},
    {"id": 23, "level_id": 3, "question_type": "single", "question_text": "扬州清曲演出中，乐队最具特色的击奏乐器是？", "option_a": "瓷碟与酒杯", "option_b": "木鱼与引磬", "option_c": "堂鼓与板", "option_d": "云锣与铙钹", "answer": "A", "analysis": "清曲乐队以瓷碟、酒杯击节，声清越。", "image": None, "difficulty": 2},
    {"id": 24, "level_id": 3, "question_type": "judge", "question_text": "扬州清曲是扬剧的重要唱腔来源之一。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "扬剧唱腔吸收了扬州清曲曲牌。", "image": None, "difficulty": 2},
    {"id": 25, "level_id": 3, "question_type": "single", "question_text": "下列哪部作品是扬剧经典保留剧目？", "option_a": "《百岁挂帅》", "option_b": "《牡丹亭》", "option_c": "《天仙配》", "option_d": "《花木兰》", "answer": "A", "analysis": "《百岁挂帅》是扬剧代表剧目。", "image": None, "difficulty": 2},
    {"id": 26, "level_id": 3, "question_type": "single", "question_text": "扬州评话经典长篇书目《水浒》的说书人被誉为什么？", "option_a": "武水浒", "option_b": "活关公", "option_c": "俏西施", "option_d": "金嗓子", "answer": "A", "analysis": "王丽堂以《水浒》享誉书坛，被誉为“武水浒”。", "image": None, "difficulty": 3},
    {"id": 27, "level_id": 3, "question_type": "image", "question_text": "下图展示的是哪项扬州非遗的演出场景？", "option_a": "杖头木偶戏", "option_b": "扬州评话", "option_c": "扬剧", "option_d": "清曲坐唱", "answer": "A", "analysis": "杖头木偶以内扦操控，演员与木偶同台表演。", "image": f"{QUIZ_IMAGE_PREFIX}/quiz-puppet.svg", "difficulty": 3},
    {"id": 28, "level_id": 3, "question_type": "judge", "question_text": "扬州清曲又称“广陵清曲”，以坐唱形式演出。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "扬州清曲又称广陵清曲，坐唱曲牌连缀。", "image": None, "difficulty": 2},
    {"id": 29, "level_id": 3, "question_type": "single", "question_text": "扬州评话中用于开场镇场、提示听众的道具是？", "option_a": "醒木", "option_b": "铜锣", "option_c": "鼓板", "option_d": "铃铛", "answer": "A", "analysis": "醒木是评话表演的重要道具。", "image": None, "difficulty": 2},
    {"id": 30, "level_id": 3, "question_type": "single", "question_text": "广陵琴派的代表性琴谱是？", "option_a": "《蕉庵琴谱》", "option_b": "《神奇秘谱》", "option_c": "《白石道人歌曲》", "option_d": "《九宫大成》", "answer": "A", "analysis": "秦维瀚《蕉庵琴谱》系统总结了广陵琴派琴学。", "image": None, "difficulty": 3},
    # ---------- 第四关：丹青圣手 ----------
    {"id": 31, "level_id": 4, "question_type": "single", "question_text": "扬州剪纸的艺术特色被概括为？", "option_a": "细、秀、雅、活", "option_b": "粗、犷、朴、拙", "option_c": "艳、丽、繁、密", "option_d": "简、淡、空、灵", "answer": "A", "analysis": "“细秀雅活”是扬州剪纸的公认风格。", "image": None, "difficulty": 2},
    {"id": 32, "level_id": 4, "question_type": "single", "question_text": "点螺是扬州漆器的哪类工艺？", "option_a": "镶嵌装饰", "option_b": "髹涂打磨", "option_c": "雕刻成型", "option_d": "编织收边", "answer": "A", "analysis": "点螺以螺钿镶嵌成纹，是漆器装饰工艺。", "image": None, "difficulty": 3},
    {"id": 33, "level_id": 4, "question_type": "judge", "question_text": "扬州玉雕在清代因盐商经济推动达到鼎盛。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "清代扬州盐商奢靡之风推动玉器业鼎盛。", "image": None, "difficulty": 2},
    {"id": 34, "level_id": 4, "question_type": "single", "question_text": "扬州刺绣擅长表现的画种风格是？", "option_a": "水墨山水", "option_b": "油画肖像", "option_c": "版画插图", "option_d": "壁画飞天", "answer": "A", "analysis": "扬州刺绣以针代笔表现水墨画的浓淡干湿。", "image": None, "difficulty": 3},
    {"id": 35, "level_id": 4, "question_type": "image", "question_text": "下图所示为哪种非遗的创作场景？", "option_a": "扬州剪纸", "option_b": "玉雕抛光", "option_c": "漆器髹涂", "option_d": "木偶制作", "answer": "A", "analysis": "图中为剪纸创作场景，一剪一染见功夫。", "image": f"{QUIZ_IMAGE_PREFIX}/quiz-papercut.svg", "difficulty": 2},
    {"id": 36, "level_id": 4, "question_type": "single", "question_text": "“剪纸绣样”的主要用途是？", "option_a": "为刺绣提供底样", "option_b": "建筑彩绘打底", "option_c": "漆器纹样拓印", "option_d": "木雕图样复制", "answer": "A", "analysis": "剪纸常用于刺绣底样，是剪纸最早的功能之一。", "image": None, "difficulty": 3},
    {"id": 37, "level_id": 4, "question_type": "judge", "question_text": "扬州漆器的“平磨螺钿”属于镶嵌类工艺。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "平磨螺钿以螺钿打磨拼嵌成图。", "image": None, "difficulty": 3},
    {"id": 38, "level_id": 4, "question_type": "single", "question_text": "扬州剪纸从用途上最早多用于？", "option_a": "刺绣样稿", "option_b": "门窗装饰", "option_c": "礼品包装", "option_d": "书籍插图", "answer": "A", "analysis": "早期剪纸多为刺绣样稿与喜庆装饰。", "image": None, "difficulty": 3},
    {"id": 39, "level_id": 4, "question_type": "single", "question_text": "下列哪种色彩体系是蓝印花布的典型特征？", "option_a": "蓝白两色", "option_b": "五彩斑斓", "option_c": "金碧辉煌", "option_d": "朱红黛绿", "answer": "A", "analysis": "蓝印花布以靛蓝染于白布，蓝白相映。", "image": None, "difficulty": 1},
    {"id": 40, "level_id": 4, "question_type": "judge", "question_text": "扬州剪纸已被列入联合国教科文组织人类非物质文化遗产代表作名录。", "option_a": "错误", "option_b": "正确", "option_c": None, "option_d": None, "answer": "A", "analysis": "列入人类非遗名录的是“中国剪纸”整体项目，扬州剪纸是其重要组成部分。", "image": None, "difficulty": 3},
    # ---------- 第五关：非遗大师 ----------
    {"id": 41, "level_id": 5, "question_type": "single", "question_text": "下列哪一组非遗项目同属扬州“传统美术”类？", "option_a": "扬州剪纸、扬州玉雕", "option_b": "扬剧、扬州评话", "option_c": "富春茶点、蓝印花布", "option_d": "高邮民歌、广陵琴派", "answer": "A", "analysis": "剪纸与玉雕均为传统美术类。", "image": None, "difficulty": 3},
    {"id": 42, "level_id": 5, "question_type": "single", "question_text": "扬州漆器“雕漆嵌玉”融合了哪两种工艺？", "option_a": "雕漆与玉石镶嵌", "option_b": "点螺与戗金", "option_c": "平磨与描金", "option_d": "剔红与剔犀", "answer": "A", "analysis": "雕漆嵌玉以雕漆为地、镶嵌玉石为饰。", "image": None, "difficulty": 3},
    {"id": 43, "level_id": 5, "question_type": "judge", "question_text": "“扬州三把刀”于2016年列入江苏省级非物质文化遗产名录。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "“三把刀”技艺列入江苏省级名录，属民俗类。", "image": None, "difficulty": 3},
    {"id": 44, "level_id": 5, "question_type": "single", "question_text": "富春茶点制作技艺中“魁龙珠”茶的窨制原料是？", "option_a": "龙井、魁针、珠兰", "option_b": "毛尖、茉莉、桂花", "option_c": "普洱、玫瑰、陈皮", "option_d": "铁观音、菊花、冰糖", "answer": "A", "analysis": "魁龙珠取龙井之味、魁针之色、珠兰之香。", "image": None, "difficulty": 3},
    {"id": 45, "level_id": 5, "question_type": "single", "question_text": "扬州非遗知识图谱中，“传承人”与“非遗项目”之间的关系类型是？", "option_a": "传承（INHERITS）", "option_b": "归属（BELONGS_TO）", "option_c": "盛行于（PREVAILED_IN）", "option_d": "关联民俗（ASSOCIATED_WITH）", "answer": "A", "analysis": "图谱中 [:INHERITS] 表示传承人对项目的传承关系。", "image": None, "difficulty": 3},
    {"id": 46, "level_id": 5, "question_type": "image", "question_text": "下图所示为下列哪种非遗项目的代表作品？", "option_a": "玉雕山子", "option_b": "剪纸", "option_c": "漆器", "option_d": "刺绣", "answer": "A", "analysis": "图中为玉雕山子，扬州玉雕擅长大型山子雕。", "image": f"{QUIZ_IMAGE_PREFIX}/quiz-jade.svg", "difficulty": 3},
    {"id": 47, "level_id": 5, "question_type": "judge", "question_text": "AI 生成的非遗风格作品在平台中会标注“AI创作”标识。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "按平台合规要求，AI 生成内容均标注“AI创作”。", "image": None, "difficulty": 1},
    {"id": 48, "level_id": 5, "question_type": "single", "question_text": "扫码导览功能中，二维码解析出的关键参数是？", "option_a": "项目ID", "option_b": "用户ID", "option_c": "音频时长", "option_d": "地图坐标", "answer": "A", "analysis": "二维码内含项目ID，扫码后跳转对应详情与讲解。", "image": None, "difficulty": 2},
    {"id": 49, "level_id": 5, "question_type": "single", "question_text": "扬州评话在表演中“一人摹拟百样角色”的表现手法称为？", "option_a": "演口", "option_b": "噱功", "option_c": "方口", "option_d": "圆口", "answer": "A", "analysis": "“演口”指演员以声口、神态摹拟各类角色。", "image": None, "difficulty": 3},
    {"id": 50, "level_id": 5, "question_type": "judge", "question_text": "平台的知识图谱数据存储于 Neo4j 图数据库中。", "option_a": "正确", "option_b": "错误", "option_c": None, "option_d": None, "answer": "A", "analysis": "非遗实体与关系存储于 Neo4j，业务数据存储于 MySQL。", "image": None, "difficulty": 2},
]

# =====================================================================
# 五、演示用户（1 个管理员 + 5 个排行榜用户，便于演示积分排行榜）
# =====================================================================
DEMO_USERS: list[dict] = [
    {"id": 1, "openid": "demo_admin", "nickname": "非遗管理员", "avatar": AVATAR_PLACEHOLDER, "score": 0},
    {"id": 2, "openid": "demo_rank_1", "nickname": "非遗小达人", "avatar": AVATAR_PLACEHOLDER, "score": 980},
    {"id": 3, "openid": "demo_rank_2", "nickname": "扬州小秀才", "avatar": AVATAR_PLACEHOLDER, "score": 860},
    {"id": 4, "openid": "demo_rank_3", "nickname": "剪纸小传人", "avatar": AVATAR_PLACEHOLDER, "score": 720},
    {"id": 5, "openid": "demo_rank_4", "nickname": "玉雕学徒", "avatar": AVATAR_PLACEHOLDER, "score": 610},
    {"id": 6, "openid": "demo_rank_5", "nickname": "早茶常客", "avatar": AVATAR_PLACEHOLDER, "score": 480},
]


def seed_if_empty() -> bool:
    """数据库为空时写入种子数据；已有数据则跳过。

    :return: True 表示执行了写入，False 表示跳过
    """
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        project_count = session.query(HeritageProject).count()
        if project_count > 0:
            logger.info("数据库已有数据（%d 个非遗项目），跳过种子初始化", project_count)
            return False
        level_count = session.query(GameLevel).count()
        if level_count > 0:
            logger.info("数据库已有关卡数据（%d 个），跳过种子初始化", level_count)
            return False
    finally:
        session.close()
    _seed()
    return True


def _seed() -> None:
    """写入全部种子数据（项目 → 传承人 → 关卡 → 题目 → 演示用户）。"""
    session = SessionLocal()
    try:
        # 1. 非遗项目
        for data in PROJECTS:
            session.add(HeritageProject(**data))
        session.flush()
        # 2. 传承人（按项目名解析外键）
        project_ids = {project.name: project.id for project in session.query(HeritageProject).all()}
        for data in INHERITORS:
            payload = {key: value for key, value in data.items() if key != "project_name"}
            payload["project_id"] = project_ids[data["project_name"]]
            session.add(Inheritor(**payload))
        # 3. 关卡
        for data in LEVELS:
            session.add(GameLevel(**data))
        # 4. 题目
        for data in QUESTIONS:
            session.add(GameQuestion(**data))
        # 5. 演示用户
        for data in DEMO_USERS:
            session.add(SysUser(**data))
        session.commit()
        logger.info(
            "种子数据写入完成：%d 个项目 / %d 位传承人 / %d 个关卡 / %d 道题目 / %d 个演示用户",
            len(PROJECTS),
            len(INHERITORS),
            len(LEVELS),
            len(QUESTIONS),
            len(DEMO_USERS),
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    """脚本入口：python -m scripts.seed_data"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    if seed_if_empty():
        logger.info("种子数据初始化成功")
    else:
        logger.info("数据库已有数据，未执行写入")


if __name__ == "__main__":
    main()
