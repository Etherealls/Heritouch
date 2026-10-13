/**
 * 扬州非遗示例数据集（Mock 数据源）
 * 数据说明：项目名称、类别、级别依据公开非遗名录整理；
 * 简介文本为演示用概括描述；传承人信息为演示数据，可在后台管理中替换。
 */

/* ---------------- 非遗分类 ---------------- */
export const categories = [
  { id: 1, name: '传统技艺', icon: '🔨', count: 4 },
  { id: 2, name: '传统美术', icon: '🎨', count: 3 },
  { id: 3, name: '传统戏剧', icon: '🎭', count: 2 },
  { id: 4, name: '传统音乐', icon: '🎵', count: 2 },
  { id: 5, name: '曲艺', icon: '📢', count: 2 },
  { id: 6, name: '民俗', icon: '🏮', count: 1 },
  { id: 7, name: '传统医药', icon: '🌿', count: 1 }
]

/* ---------------- 非遗项目 ---------------- */
export const projects = [
  {
    id: 1,
    name: '扬州剪纸',
    level: '国家级',
    category: '传统美术',
    region: '江苏扬州',
    batch: 2006,
    cover_image: '/static/images/paper-cut.jpg',
    intro: '扬州剪纸是南方剪纸艺术的代表流派之一，以“细、秀、雅、活”著称，题材涵盖花鸟虫鱼、戏曲人物与民俗生活，尤以“剪纸绣样”最具特色。',
    history: '扬州剪纸源于唐宋，兴盛于明清。清代扬州盐商云集，民俗活动兴盛，剪纸广泛应用于刺绣样稿、喜庆装饰与灯彩制作，逐渐形成秀美灵动的艺术风格。',
    craft: '选纸→起稿→剪刻→点染。艺人以宣纸或彩纸为料，运以尖口小剪，线条细如发丝；点色剪纸采用“一手剪、一手染”技法，色彩晕染自然。',
    tags: ['第一批国家级', '传统美术', '示范性流派'],
    audio_mandarin: '/static/audio/jianzhi-mandarin.mp3',
    audio_dialect: '/static/audio/jianzhi-dialect.mp3',
    latitude: 32.394,
    longitude: 119.412,
    inheritors: [101, 102],
    materials: ['宣纸', '彩纸', '剪刀'],
    works: ['《百鸟朝凤》剪纸屏风', '《扬州八怪》故事剪纸'],
    folk_customs: ['春节剪窗花', '婚嫁剪喜花']
  },
  {
    id: 2,
    name: '扬州玉雕',
    level: '国家级',
    category: '传统美术',
    region: '江苏扬州',
    batch: 2006,
    cover_image: '/static/images/jade-carving.jpg',
    intro: '扬州玉雕以“浑厚、圆润、儒雅、灵秀”见长，讲究“因料施艺、量材取形”，尤其擅长大型山子雕，被誉为中国玉雕的“南派”代表。',
    history: '扬州琢玉工艺可追溯至四千年前的江淮新石器时代；两汉、隋唐持续发展，明清因盐商经济推动达到鼎盛，“扬州工”名扬天下。',
    craft: '相玉→设计→琢碾→细作→抛光。先审石度色、因形就势，再以铡、錾、冲、轧等技法层层推进，最后精细打磨显玉质温润。',
    tags: ['第一批国家级', '传统美术', '山子雕'],
    audio_mandarin: '/static/audio/yudiao-mandarin.mp3',
    audio_dialect: '/static/audio/yudiao-dialect.mp3',
    latitude: 32.391,
    longitude: 119.421,
    inheritors: [103],
    materials: ['和田玉', '翡翠', '岫岩玉'],
    works: ['《大禹治水图》玉山', '《聚珍图》碧玉山子'],
    folk_customs: ['玉器庙会']
  },
  {
    id: 3,
    name: '扬州漆器髹饰技艺',
    level: '国家级',
    category: '传统技艺',
    region: '江苏扬州',
    batch: 2006,
    cover_image: '/static/images/lacquerware.jpg',
    intro: '扬州漆器造型古朴典雅，工艺精湛繁复，综合运用雕漆、点螺、平磨螺钿等“十大工艺”，是中国漆器艺术的高峰。',
    history: '扬州漆器起源于战国，汉代广陵漆器已负盛名；唐代“金银平脱”、宋代“雕红漆”、明清雕漆嵌玉鼎盛，清代为宫廷御用贡品。',
    craft: '制胎→髹漆→打磨→装饰。一件雕漆作品需髹涂数十至数百道漆，每道须在窨房中阴干，再行刀刻，耗时可达数年。',
    tags: ['第一批国家级', '传统技艺', '雕漆嵌玉'],
    audio_mandarin: '/static/audio/qiqi-mandarin.mp3',
    audio_dialect: '/static/audio/qiqi-dialect.mp3',
    latitude: 32.398,
    longitude: 119.435,
    inheritors: [104, 105],
    materials: ['大漆', '螺钿', '金银箔', '楠木胎'],
    works: ['《松鹤延年》雕漆地屏', '点螺《锦绣河山》漆器屏风'],
    folk_customs: ['嫁女陪嫁漆器家具']
  },
  {
    id: 4,
    name: '扬州评话',
    level: '国家级',
    category: '曲艺',
    region: '江苏扬州',
    batch: 2006,
    cover_image: '/static/images/pinghua.jpg',
    intro: '扬州评话以扬州方言说表，讲究“口、手、眼、身、步”五功，长篇书目众多，是扬州书场的代表性曲种。',
    history: '扬州评话形成于明末清初，与扬州运河商业繁荣、书场文化兴盛密切相关，清乾隆年间达到高峰，名家辈出。',
    craft: '坐唱→说表→演口→噱功。演员一人摹拟百样角色，以折扇、醒木为道具，方口与圆口结合，叙事中夹评夹议。',
    tags: ['第一批国家级', '曲艺', '书场文化'],
    audio_mandarin: '/static/audio/pinghua-mandarin.mp3',
    audio_dialect: '/static/audio/pinghua-dialect.mp3',
    latitude: 32.402,
    longitude: 119.418,
    inheritors: [106],
    materials: ['折扇', '醒木'],
    works: ['《水浒》评话系列', '《三国》评话系列'],
    folk_customs: ['茶馆听书']
  },
  {
    id: 5,
    name: '扬剧',
    level: '国家级',
    category: '传统戏剧',
    region: '江苏扬州',
    batch: 2006,
    cover_image: '/static/images/yangju.jpg',
    intro: '扬剧由扬州花鼓戏、香火戏与扬州清曲融合发展而成，唱腔清新华丽、生活气息浓郁，是江苏代表性地方戏曲剧种之一。',
    history: '扬剧发端于清代扬州民间花鼓与香火会戏，民国年间进入上海演出后定名“扬剧”，逐渐形成完整的行当与唱腔体系。',
    craft: '唱→念→做→打。以“大开口”“小开口”为基础唱腔，兼收民歌小调，表演文武兼备、诙谐生动。',
    tags: ['第一批国家级', '传统戏剧', '江苏代表剧种'],
    audio_mandarin: '/static/audio/yangju-mandarin.mp3',
    audio_dialect: '/static/audio/yangju-dialect.mp3',
    latitude: 32.405,
    longitude: 119.424,
    inheritors: [107],
    materials: ['戏曲服饰', '锣鼓弦乐'],
    works: ['《百岁挂帅》', '《珍珠塔》'],
    folk_customs: ['庙会戏台演出']
  },
  {
    id: 6,
    name: '扬州清曲',
    level: '国家级',
    category: '曲艺',
    region: '江苏扬州',
    batch: 2006,
    cover_image: '/static/images/qingqu.jpg',
    intro: '扬州清曲又称“扬州小曲”或“广陵清曲”，以坐唱形式演出，曲牌丰富、唱腔婉转，被誉为“里下河音乐的活化石”。',
    history: '扬州清曲源于元代小唱，明清时期吸收各地小曲在扬州融汇定型，清末民初最为流行，后成为扬剧的重要唱腔来源。',
    craft: '坐唱→夹白→帮腔。乐队以琵琶、三弦、二胡、酒杯与瓷碟为器，击碟声清越，曲牌连缀叙事。',
    tags: ['第一批国家级', '曲艺', '曲牌连缀体'],
    audio_mandarin: '/static/audio/qingqu-mandarin.mp3',
    audio_dialect: '/static/audio/qingqu-dialect.mp3',
    latitude: 32.399,
    longitude: 119.409,
    inheritors: [108],
    materials: ['琵琶', '三弦', '瓷碟', '酒杯'],
    works: ['《扬州月》清曲组歌', '《茉莉花》早期曲调遗存'],
    folk_customs: ['堂会唱曲']
  },
  {
    id: 7,
    name: '古琴艺术（广陵琴派）',
    level: '国家级',
    category: '传统音乐',
    region: '江苏扬州',
    batch: 2008,
    cover_image: '/static/images/guqin.jpg',
    intro: '广陵琴派是中国古琴最具影响力的流派之一，风格“跌宕多变、刚柔相济”，指法细腻，代表曲目多与扬州文化意象相关。',
    history: '广陵琴派形成于清代扬州，以徐常遇为代表开创，经秦维瀚《蕉庵琴谱》系统化，近现代张子谦、刘少椿等名家薪火相传。',
    craft: '识谱→指法→吟猱→会意。演奏讲究“重弦轻捻”，以吟猱绰注表现山水意境，琴曲多寄情江南风月。',
    tags: ['第二批国家级', '传统音乐', '人类非遗代表作'],
    audio_mandarin: '/static/audio/guqin-mandarin.mp3',
    audio_dialect: '/static/audio/guqin-dialect.mp3',
    latitude: 32.396,
    longitude: 119.445,
    inheritors: [109],
    materials: ['桐木面板', '梓木底板', '蚕丝弦'],
    works: ['《平沙落雁》', '《梅花三弄》'],
    folk_customs: ['文人雅集']
  },
  {
    id: 8,
    name: '扬州刺绣',
    level: '省级',
    category: '传统美术',
    region: '江苏扬州',
    batch: 2007,
    cover_image: '/static/images/embroidery.jpg',
    intro: '扬州刺绣以“仿古绣”与“水墨绣”著称，针法多变、绣理细腻，善于表现书画笔墨的浓淡干湿，有“针画”之誉。',
    history: '扬州刺绣自汉代发端，宋代已有专业化绣坊，清代与扬州画派互动密切，形成以绣仿画、画绣结合的地方特色。',
    craft: '设计→上绷→配线→刺绣→装裱。以针代笔、以线代墨，一件仿古绣作品需运用数十种针法层层晕染。',
    tags: ['江苏省级', '传统美术', '仿古山水绣'],
    audio_mandarin: '/static/audio/cixiu-mandarin.mp3',
    audio_dialect: '/static/audio/cixiu-dialect.mp3',
    latitude: 32.388,
    longitude: 119.428,
    inheritors: [110],
    materials: ['绢', '桑蚕丝线', '绷架'],
    works: ['《韩熙载夜宴图》刺绣长卷', '《富春山居图》仿古绣'],
    folk_customs: ['嫁女绣帐']
  },
  {
    id: 9,
    name: '蓝印花布印染技艺',
    level: '省级',
    category: '传统技艺',
    region: '江苏扬州',
    batch: 2007,
    cover_image: '/static/images/blue-calico.jpg',
    intro: '扬州蓝印花布以天然蓝草发酵染色，图案朴素典雅，蓝白相映，广泛用于被面、帐檐、服饰与民俗用品。',
    history: '蓝印花布在江淮地区流传久远，清代扬州为重要产销地，染坊林立，“扬州蓝”与“南通蓝”并称江苏蓝印花布两大系统。',
    craft: '刻版→刮浆→浸染→刮灰→漂洗。以黄豆粉加石灰防染，靛缸低温多次浸染，蓝度逐日加深。',
    tags: ['江苏省级', '传统技艺', '天然植物染'],
    audio_mandarin: '/static/audio/lanyin-mandarin.mp3',
    audio_dialect: '/static/audio/lanyin-dialect.mp3',
    latitude: 32.407,
    longitude: 119.401,
    inheritors: [111],
    materials: ['蓝草', '土白布', '豆粉', '石灰'],
    works: ['《凤穿牡丹》蓝印花布被面', '《五福捧寿》帐檐'],
    folk_customs: ['婚嫁备蓝印花布嫁妆']
  },
  {
    id: 10,
    name: '富春茶点制作技艺',
    level: '国家级',
    category: '传统技艺',
    region: '江苏扬州',
    batch: 2008,
    cover_image: '/static/images/fuchun-tea.jpg',
    intro: '富春茶点以“魁龙珠”茶与三丁包、翡翠烧卖等细点闻名，讲究“茶以点心佐、点以茶兴味”，是扬州早茶文化的代表。',
    history: '富春茶社创于清代光绪年间，百年间形成“花、茶、点、菜”结合的淮扬茶食体系，“早上皮包水”的扬州生活习俗由此传扬。',
    craft: '和面→制馅→包捏→醒发→蒸制。三丁包讲究“鸡丁大、笋丁脆、肉丁香”，擀皮要求“底厚边薄”十八道褶。',
    tags: ['第二批国家级', '传统技艺', '扬州早茶'],
    audio_mandarin: '/static/audio/fuchun-mandarin.mp3',
    audio_dialect: '/static/audio/fuchun-dialect.mp3',
    latitude: 32.393,
    longitude: 119.416,
    inheritors: [112],
    materials: ['面粉', '西湖龙井', '魁针', '珠兰'],
    works: ['三丁包', '翡翠烧卖', '魁龙珠茶'],
    folk_customs: ['扬州早茶']
  },
  {
    id: 11,
    name: '杖头木偶戏（扬州杖头木偶）',
    level: '省级',
    category: '传统戏剧',
    region: '江苏扬州',
    batch: 2007,
    cover_image: '/static/images/puppet.jpg',
    intro: '扬州杖头木偶以“内扦”结构为特色，木偶可眼珠转动、口唇开合，表演细腻传神，尤擅武戏与特技。',
    history: '扬州木偶戏起源于清代泰兴、兴化一带的“傀儡戏”，20世纪50年代扬州市木偶剧团成立后艺术体系日趋完备。',
    craft: '举→转→捻→勾。演员以三根扦子操控木偶头、双手，配合身段步法，做到“人偶合一”。',
    tags: ['江苏省级', '传统戏剧', '内扦木偶'],
    audio_mandarin: '/static/audio/muou-mandarin.mp3',
    audio_dialect: '/static/audio/muou-dialect.mp3',
    latitude: 32.412,
    longitude: 119.430,
    inheritors: [113],
    materials: ['樟木', '锦缎', '丝线'],
    works: ['《嫦娥奔月》', '《火焰山》'],
    folk_customs: ['节庆木偶戏台']
  },
  {
    id: 12,
    name: '高邮民歌',
    level: '省级',
    category: '传统音乐',
    region: '江苏扬州（高邮）',
    batch: 2007,
    cover_image: '/static/images/gaoyou-folk.jpg',
    intro: '高邮民歌里下河风格浓郁，号子、小调、情歌并存，《数鸭蛋》《撒趟子撂在外》等曲目流传甚广。',
    history: '高邮地处里下河水网地带，秧歌、车水号子、渔歌在劳作中世代传唱，20世纪50年代起经系统采集整理登上全国舞台。',
    craft: '领唱→和腔→对歌。一唱众和、即兴填词，曲调随水乡劳作节奏起伏。',
    tags: ['江苏省级', '传统音乐', '里下河民歌'],
    audio_mandarin: '/static/audio/gaoyou-mandarin.mp3',
    audio_dialect: '/static/audio/gaoyou-dialect.mp3',
    latitude: 32.784,
    longitude: 119.459,
    inheritors: [114],
    materials: ['民歌曲调', '方言唱词'],
    works: ['《数鸭蛋》', '《撒趟子撂在外》'],
    folk_customs: ['秧歌会']
  },
  {
    id: 13,
    name: '扬州“三把刀”技艺',
    level: '省级',
    category: '民俗',
    region: '江苏扬州',
    batch: 2007,
    cover_image: '/static/images/three-knives.jpg',
    intro: '“扬州三把刀”指厨刀、修脚刀、剃头刀，集中体现扬州生活技艺的精巧，是扬州澡堂文化与早茶习俗的活态载体。',
    history: '清代扬州盐商奢靡之风带动服务业兴盛，“上午皮包水、下午水包皮”的习俗孕育出精湛的厨艺与修脚、理发技艺。',
    craft: '厨刀→淮扬菜刀工；修脚刀→斫、断、劈、片；剃头刀→剃、修、推、捏。',
    tags: ['江苏省级', '民俗', '生活技艺'],
    audio_mandarin: '/static/audio/sandao-mandarin.mp3',
    audio_dialect: '/static/audio/sandao-dialect.mp3',
    latitude: 32.389,
    longitude: 119.404,
    inheritors: [115],
    materials: ['厨刀', '修脚刀', '剃头刀'],
    works: ['大煮干丝刀工', '陆三足艺'],
    folk_customs: ['扬州澡堂文化', '扬州早茶']
  },
  {
    id: 14,
    name: '夏氏内科疗法（扬州中医）',
    level: '省级',
    category: '传统医药',
    region: '江苏扬州',
    batch: 2016,
    cover_image: '/static/images/tcm.jpg',
    intro: '夏氏内科以“轻可去实”的用药风格著称，擅长外感热病与脾胃病诊治，为扬州中医世家医术的代表。',
    history: '夏氏内科发端于清末扬州中医世家，历经数代传承，形成以“简、便、验、廉”为特色的诊疗经验体系。',
    craft: '四诊合参→辨证立法→遣方用药。强调因地因人制宜，药味精简、轻清灵动。',
    tags: ['江苏省级', '传统医药', '中医世家'],
    audio_mandarin: '/static/audio/tcm-mandarin.mp3',
    audio_dialect: '/static/audio/tcm-dialect.mp3',
    latitude: 32.401,
    longitude: 119.437,
    inheritors: [116],
    materials: ['中草药', '汤剂'],
    works: ['夏氏验方集'],
    folk_customs: ['冬令进补膏方']
  }
]

/* ---------------- 传承人（演示数据） ---------------- */
export const inheritors = [
  { id: 101, name: '张秀芳', project_id: 1, title: '国家级代表性传承人', gender: '女', biography: '扬州剪纸代表性传承人，以点色剪纸见长，作品构图精巧、线条流畅，长期致力于剪纸进校园传承活动。', photo: '/static/images/person-1.jpg' },
  { id: 102, name: '熊崇荣', project_id: 1, title: '市级代表性传承人', gender: '男', biography: '从事剪纸创作四十余年，擅长民俗题材大幅剪纸创作，多次在各类非遗展演中现场献艺。', photo: '/static/images/person-2.jpg' },
  { id: 103, name: '江春', project_id: 2, title: '国家级代表性传承人', gender: '男', biography: '扬州玉雕名家，精于山子雕与人物件，主张“因料施艺”，作品多次获中国工艺美术百花奖。', photo: '/static/images/person-3.jpg' },
  { id: 104, name: '张来喜', project_id: 3, title: '国家级代表性传承人', gender: '男', biography: '扬州漆器雕漆工艺代表性传承人，掌握雕漆嵌玉核心技艺，作品气势恢宏、刀法深峻。', photo: '/static/images/person-4.jpg' },
  { id: 105, name: '池家骏', project_id: 3, title: '市级代表性传承人', gender: '男', biography: '扬州漆器点螺工艺传承人，专注传统髹饰技艺的恢复与创新，尤擅点螺屏风制作。', photo: '/static/images/person-5.jpg' },
  { id: 106, name: '王丽堂', project_id: 4, title: '国家级代表性传承人', gender: '女', biography: '扬州评话名家，以《水浒》系列书目享誉书坛，说口清脆、形神兼备，被誉为“武水浒”的代表。', photo: '/static/images/person-6.jpg' },
  { id: 107, name: '李开敏', project_id: 5, title: '省级代表性传承人', gender: '女', biography: '扬剧表演艺术家，唱腔婉转清丽，代表作《百岁挂帅》《恩仇记》，致力于扬剧青年演员培养。', photo: '/static/images/person-7.jpg' },
  { id: 108, name: '聂峰', project_id: 6, title: '省级代表性传承人', gender: '男', biography: '扬州清曲演唱与研究专家，整理大量传统曲牌，推动清曲进校园与数字化传播。', photo: '/static/images/person-8.jpg' },
  { id: 109, name: '马维衡', project_id: 7, title: '省级代表性传承人', gender: '男', biography: '广陵琴派琴家，擅弹《平沙落雁》《山居吟》，致力于古琴制作技艺研究与琴学传承。', photo: '/static/images/person-9.jpg' },
  { id: 110, name: '卫芳', project_id: 8, title: '市级代表性传承人', gender: '女', biography: '扬州刺绣传承人，专攻仿古山水绣与水墨绣，作品以针法细腻、绣理自然见长。', photo: '/static/images/person-10.jpg' },
  { id: 111, name: '王稳扬', project_id: 9, title: '市级代表性传承人', gender: '男', biography: '蓝印花布印染技艺传承人，坚持古法靛蓝发酵与手工刮浆，产品远销海内外。', photo: '/static/images/person-11.jpg' },
  { id: 112, name: '徐永珍', project_id: 10, title: '国家级代表性传承人', gender: '女', biography: '富春茶点制作技艺代表性传承人，精通包子、烧卖等淮扬细点制作，被誉为“点心状元”。', photo: '/static/images/person-12.jpg' },
  { id: 113, name: '封春来', project_id: 11, title: '市级代表性传承人', gender: '男', biography: '扬州杖头木偶操控技艺传承人，擅长武戏与木偶特技表演，多次随团出国演出。', photo: '/static/images/person-13.jpg' },
  { id: 114, name: '王兰英', project_id: 12, title: '省级代表性传承人', gender: '女', biography: '高邮民歌演唱家，嗓音高亢嘹亮，擅长秧歌号子与情歌对唱，积极辅导乡村民歌手。', photo: '/static/images/person-14.jpg' },
  { id: 115, name: '陆琴', project_id: 13, title: '市级代表性传承人', gender: '女', biography: '扬州修脚技艺代表性传承人，创立“陆氏修脚术”，以“稳、轻、准”著称。', photo: '/static/images/person-15.jpg' },
  { id: 116, name: '夏雨生', project_id: 14, title: '市级代表性传承人', gender: '男', biography: '夏氏内科传人，临床擅用轻清灵动之剂调理脾胃与外感热病。', photo: '/static/images/person-16.jpg' }
]

/* ---------------- 知识图谱（节点 + 关系） ---------------- */
/* 关系类型（文档 4.1.3 预设 9 类核心关系的子集）：
   INHERITS 传承人→项目 / BELONGS_TO_CATEGORY 项目→类别 / PREVAILED_IN 项目→朝代
   USES_MATERIAL 项目→材料 / CREATED 传承人→作品 / ASSOCIATED_WITH 项目→民俗 */
export const graphData = {
  nodes: [
    // 非遗项目
    ...projects.map((p) => ({ id: 'h' + p.id, name: p.name, type: 'heritage', refId: p.id })),
    // 类别
    ...categories.map((c) => ({ id: 'c' + c.id, name: c.name, type: 'category' })),
    // 传承人
    ...inheritors.map((i) => ({ id: 'i' + i.id, name: i.name, type: 'inheritor', refId: i.id })),
    // 朝代
    { id: 'd1', name: '唐宋', type: 'dynasty' },
    { id: 'd2', name: '明清', type: 'dynasty' },
    { id: 'd3', name: '近现代', type: 'dynasty' },
    // 材料
    { id: 'm1', name: '宣纸彩纸', type: 'material' },
    { id: 'm2', name: '和田玉石', type: 'material' },
    { id: 'm3', name: '大漆螺钿', type: 'material' },
    // 民俗
    { id: 'f1', name: '扬州早茶', type: 'folk_custom' },
    { id: 'f2', name: '春节窗花', type: 'folk_custom' },
    { id: 'f3', name: '澡堂文化', type: 'folk_custom' }
  ],
  edges: [
    // 项目 → 类别
    { source: 'h1', target: 'c2', label: '归属' },
    { source: 'h2', target: 'c2', label: '归属' },
    { source: 'h3', target: 'c1', label: '归属' },
    { source: 'h4', target: 'c5', label: '归属' },
    { source: 'h5', target: 'c3', label: '归属' },
    { source: 'h6', target: 'c5', label: '归属' },
    { source: 'h7', target: 'c4', label: '归属' },
    { source: 'h8', target: 'c2', label: '归属' },
    { source: 'h9', target: 'c1', label: '归属' },
    { source: 'h10', target: 'c1', label: '归属' },
    { source: 'h11', target: 'c3', label: '归属' },
    { source: 'h12', target: 'c4', label: '归属' },
    { source: 'h13', target: 'c6', label: '归属' },
    { source: 'h14', target: 'c7', label: '归属' },
    // 传承人 → 项目
    { source: 'i101', target: 'h1', label: '传承' },
    { source: 'i102', target: 'h1', label: '传承' },
    { source: 'i103', target: 'h2', label: '传承' },
    { source: 'i104', target: 'h3', label: '传承' },
    { source: 'i105', target: 'h3', label: '传承' },
    { source: 'i106', target: 'h4', label: '传承' },
    { source: 'i107', target: 'h5', label: '传承' },
    { source: 'i108', target: 'h6', label: '传承' },
    { source: 'i109', target: 'h7', label: '传承' },
    { source: 'i110', target: 'h8', label: '传承' },
    { source: 'i111', target: 'h9', label: '传承' },
    { source: 'i112', target: 'h10', label: '传承' },
    { source: 'i113', target: 'h11', label: '传承' },
    { source: 'i114', target: 'h12', label: '传承' },
    { source: 'i115', target: 'h13', label: '传承' },
    { source: 'i116', target: 'h14', label: '传承' },
    // 项目 → 朝代
    { source: 'h1', target: 'd1', label: '盛行于' },
    { source: 'h2', target: 'd2', label: '盛行于' },
    { source: 'h3', target: 'd2', label: '盛行于' },
    { source: 'h4', target: 'd2', label: '盛行于' },
    { source: 'h5', target: 'd3', label: '盛行于' },
    { source: 'h7', target: 'd2', label: '盛行于' },
    { source: 'h10', target: 'd3', label: '盛行于' },
    // 项目 → 材料
    { source: 'h1', target: 'm1', label: '使用材料' },
    { source: 'h2', target: 'm2', label: '使用材料' },
    { source: 'h3', target: 'm3', label: '使用材料' },
    // 项目 → 民俗
    { source: 'h1', target: 'f2', label: '关联民俗' },
    { source: 'h10', target: 'f1', label: '关联民俗' },
    { source: 'h13', target: 'f1', label: '关联民俗' },
    { source: 'h13', target: 'f3', label: '关联民俗' }
  ]
}

/* ---------------- 科普闯关：关卡与段位 ---------------- */
export const gameLevels = [
  {
    id: 1,
    name: '入门学徒',
    subtitle: '初识扬州非遗',
    rank: '学徒',
    need_score: 0,
    theme: '基础认知',
    question_count: 10,
    icon: '🌱'
  },
  {
    id: 2,
    name: '匠人弟子',
    subtitle: '技艺门类辨一辨',
    rank: '弟子',
    need_score: 100,
    theme: '传统技艺',
    question_count: 10,
    icon: '🔨'
  },
  {
    id: 3,
    name: '曲苑知音',
    subtitle: '戏曲曲艺听门道',
    rank: '弟子',
    need_score: 250,
    theme: '戏剧曲艺',
    question_count: 10,
    icon: '🎭'
  },
  {
    id: 4,
    name: '丹青圣手',
    subtitle: '美术与图案的世界',
    rank: '匠人',
    need_score: 450,
    theme: '传统美术',
    question_count: 10,
    icon: '🖌️'
  },
  {
    id: 5,
    name: '非遗大师',
    subtitle: '综合大闯关',
    rank: '大师',
    need_score: 700,
    theme: '综合进阶',
    question_count: 10,
    icon: '🏆'
  }
]

/* ---------------- 题库（单选 / 判断 / 识图） ---------------- */
export const questions = [
  // 第一关：入门学徒
  { id: 1, level_id: 1, question_type: 'single', question_text: '扬州剪纸属于下列哪一类非遗？', option_a: '传统美术', option_b: '传统戏剧', option_c: '传统医药', option_d: '民俗', answer: 'A', analysis: '扬州剪纸是国家级传统美术类非遗，以细秀雅活著称。', difficulty: 1 },
  { id: 2, level_id: 1, question_type: 'judge', question_text: '扬州玉雕以大型山子雕见长，被誉为中国玉雕“南派”代表。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '扬州玉雕讲究因料施艺，山子雕是其标志性品类。', difficulty: 1 },
  { id: 3, level_id: 1, question_type: 'single', question_text: '“早上皮包水、下午水包皮”描述的是扬州哪种生活习俗？', option_a: '早茶与澡堂文化', option_b: '庙会与集市', option_c: '农耕与渔猎', option_d: '书院与科举', answer: 'A', analysis: '该俗语对应扬州早茶与澡堂文化，是“三把刀”技艺的生活土壤。', difficulty: 1 },
  { id: 4, level_id: 1, question_type: 'single', question_text: '富春茶点制作技艺中最具代表性的茶叶是？', option_a: '魁龙珠', option_b: '铁观音', option_c: '普洱', option_d: '大红袍', answer: 'A', analysis: '魁龙珠由龙井、魁针、珠兰窨制而成，是富春茶社的代表茶。', difficulty: 1 },
  { id: 5, level_id: 1, question_type: 'judge', question_text: '扬剧是由扬州花鼓戏、香火戏与扬州清曲融合发展而成的地方戏曲。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '扬剧融合花鼓戏、香火戏与清曲，是江苏代表性剧种。', difficulty: 1 },
  { id: 6, level_id: 1, question_type: 'single', question_text: '下列哪一项是扬州漆器的标志性工艺？', option_a: '雕漆嵌玉', option_b: '景泰蓝掐丝', option_c: '景德镇青花', option_d: '龙泉哥窑', answer: 'A', analysis: '扬州漆器综合雕漆、点螺、平磨螺钿等工艺，雕漆嵌玉最具特色。', difficulty: 1 },
  { id: 7, level_id: 1, question_type: 'image', question_text: '下图所示为哪种扬州非遗技艺的作品？', option_a: '漆器髹饰', option_b: '蓝印花布', option_c: '剪纸', option_d: '玉雕', image: '/static/images/quiz-lacquer.jpg', answer: 'A', analysis: '图中作品为雕漆嵌玉风格，是扬州漆器的典型样式。', difficulty: 1 },
  { id: 8, level_id: 1, question_type: 'single', question_text: '扬州评话表演时使用的道具组合是？', option_a: '折扇与醒木', option_b: '三弦与鼓板', option_c: '二胡与琵琶', option_d: '锣鼓与唢呐', answer: 'A', analysis: '扬州评话以折扇、醒木为道具，讲究口手眼身步五功。', difficulty: 1 },
  { id: 9, level_id: 1, question_type: 'judge', question_text: '高邮民歌是流传于扬州里下河水乡的民歌系统。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '高邮民歌为江苏省级非遗，里下河风格浓郁。', difficulty: 1 },
  { id: 10, level_id: 1, question_type: 'single', question_text: '扬州刺绣最负盛名的品类是？', option_a: '仿古绣', option_b: '苏绣双面绣', option_c: '湘绣狮虎', option_d: '粤绣金线', answer: 'A', analysis: '扬州刺绣以仿古绣和水墨绣著称，善于表现书画笔墨意趣。', difficulty: 1 },
  // 第二关：匠人弟子
  { id: 11, level_id: 2, question_type: 'single', question_text: '蓝印花布印染中起防染作用的材料是？', option_a: '黄豆粉加石灰', option_b: '蜂蜡', option_c: '松香', option_d: '面粉糊', answer: 'A', analysis: '黄豆粉加石灰刮浆形成防染层，靛缸浸染后呈蓝白花纹。', difficulty: 2 },
  { id: 12, level_id: 2, question_type: 'judge', question_text: '一件雕漆作品往往需要髹涂数十至数百道大漆。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '雕漆需层层髹涂、道道阴干，耗时可达数年。', difficulty: 2 },
  { id: 13, level_id: 2, question_type: 'single', question_text: '富春三丁包的“三丁”不包括下列哪一项？', option_a: '笋丁', option_b: '鸡丁', option_c: '肉丁', option_d: '虾丁', answer: 'D', analysis: '三丁指鸡丁、肉丁、笋丁，讲究鸡丁大、笋丁脆、肉丁香。', difficulty: 2 },
  { id: 14, level_id: 2, question_type: 'single', question_text: '广陵琴派是中国古琴的重要流派，其艺术风格被概括为？', option_a: '跌宕多变、刚柔相济', option_b: '苍古雄健', option_c: '细腻婉约如吴语', option_d: '高亢激越', answer: 'A', analysis: '广陵琴派风格跌宕多变、刚柔相济，指法细腻。', difficulty: 2 },
  { id: 15, level_id: 2, question_type: 'single', question_text: '扬州“三把刀”指的是？', option_a: '厨刀、修脚刀、剃头刀', option_b: '菜刀、剪刀、镰刀', option_c: '刻刀、剪刀、裁纸刀', option_d: '厨刀、剪刀、修脚刀', answer: 'A', analysis: '三把刀集中体现扬州生活服务业技艺的精巧。', difficulty: 2 },
  { id: 16, level_id: 2, question_type: 'image', question_text: '下图所示为哪种非遗的典型图案？', option_a: '蓝印花布', option_b: '玉雕', option_c: '漆器', option_d: '木偶', image: '/static/images/quiz-calico.jpg', answer: 'A', analysis: '图中为蓝印花布经典图案，蓝白相映。', difficulty: 2 },
  { id: 17, level_id: 2, question_type: 'judge', question_text: '扬州剪纸的“点色剪纸”采用“一手剪、一手染”技法。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '点色剪纸染色自然灵动，是扬州剪纸特色技法。', difficulty: 2 },
  { id: 18, level_id: 2, question_type: 'single', question_text: '扬州杖头木偶的结构特点是？', option_a: '内扦', option_b: '外扦', option_c: '提线', option_d: '布袋', answer: 'A', analysis: '扬州杖头木偶以内扦结构为特色，可眼转口开。', difficulty: 2 },
  { id: 19, level_id: 2, question_type: 'single', question_text: '下列哪种材料不是扬州漆器髹饰的常用材料？', option_a: '景德镇瓷土', option_b: '大漆', option_c: '螺钿', option_d: '金银箔', answer: 'A', analysis: '漆器以大漆、螺钿、金银箔等为材，与瓷土无关。', difficulty: 2 },
  { id: 20, level_id: 2, question_type: 'judge', question_text: '扬州玉雕讲究“因料施艺、量材取形”。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '因料施艺是扬州玉雕的核心创作原则。', difficulty: 2 },
  // 第三关：曲苑知音
  { id: 21, level_id: 3, question_type: 'single', question_text: '扬州评话说表时讲究“五功”，指的是？', option_a: '口、手、眼、身、步', option_b: '说、学、逗、唱、演', option_c: '唱、念、做、打、翻', option_d: '吹、拉、弹、打、舞', answer: 'A', analysis: '扬州评话五功为口手眼身步。', difficulty: 2 },
  { id: 22, level_id: 3, question_type: 'single', question_text: '扬剧的两大基础唱腔系统是？', option_a: '大开口与小开口', option_b: '皮黄与梆子', option_c: '高腔与昆腔', option_d: '评弹与宣卷', answer: 'A', analysis: '扬剧唱腔以“大开口”“小开口”为基础，兼收民歌小调。', difficulty: 2 },
  { id: 23, level_id: 3, question_type: 'single', question_text: '扬州清曲演出中，乐队最具特色的击奏乐器是？', option_a: '瓷碟与酒杯', option_b: '木鱼与引磬', option_c: '堂鼓与板', option_d: '云锣与铙钹', answer: 'A', analysis: '清曲乐队以瓷碟、酒杯击节，声清越。', difficulty: 2 },
  { id: 24, level_id: 3, question_type: 'judge', question_text: '扬州清曲是扬剧的重要唱腔来源之一。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '扬剧唱腔吸收了扬州清曲曲牌。', difficulty: 2 },
  { id: 25, level_id: 3, question_type: 'single', question_text: '下列哪部作品是扬剧经典保留剧目？', option_a: '《百岁挂帅》', option_b: '《牡丹亭》', option_c: '《天仙配》', option_d: '《花木兰》', answer: 'A', analysis: '《百岁挂帅》是扬剧代表剧目。', difficulty: 2 },
  { id: 26, level_id: 3, question_type: 'single', question_text: '扬州评话经典长篇书目《水浒》的说书人被誉为什么？', option_a: '武水浒', option_b: '活关公', option_c: '俏西施', option_d: '金嗓子', answer: 'A', analysis: '王丽堂以《水浒》享誉书坛，被誉为“武水浒”。', difficulty: 3 },
  { id: 27, level_id: 3, question_type: 'image', question_text: '下图展示的是哪项扬州非遗的演出场景？', option_a: '杖头木偶戏', option_b: '扬州评话', option_c: '扬剧', option_d: '清曲坐唱', image: '/static/images/quiz-puppet.jpg', answer: 'A', analysis: '杖头木偶以内扦操控，演员与木偶同台表演。', difficulty: 3 },
  { id: 28, level_id: 3, question_type: 'judge', question_text: '扬州清曲又称“广陵清曲”，以坐唱形式演出。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '扬州清曲又称广陵清曲，坐唱曲牌连缀。', difficulty: 2 },
  { id: 29, level_id: 3, question_type: 'single', question_text: '扬州评话中用于开场镇场、提示听众的道具是？', option_a: '醒木', option_b: '铜锣', option_c: '鼓板', option_d: '铃铛', answer: 'A', analysis: '醒木是评话表演的重要道具。', difficulty: 2 },
  { id: 30, level_id: 3, question_type: 'single', question_text: '广陵琴派的代表性琴谱是？', option_a: '《蕉庵琴谱》', option_b: '《神奇秘谱》', option_c: '《白石道人歌曲》', option_d: '《九宫大成》', answer: 'A', analysis: '秦维瀚《蕉庵琴谱》系统总结了广陵琴派琴学。', difficulty: 3 },
  // 第四关：丹青圣手
  { id: 31, level_id: 4, question_type: 'single', question_text: '扬州剪纸的艺术特色被概括为？', option_a: '细、秀、雅、活', option_b: '粗、犷、朴、拙', option_c: '艳、丽、繁、密', option_d: '简、淡、空、灵', answer: 'A', analysis: '“细秀雅活”是扬州剪纸的公认风格。', difficulty: 2 },
  { id: 32, level_id: 4, question_type: 'single', question_text: '点螺是扬州漆器的哪类工艺？', option_a: '镶嵌装饰', option_b: '髹涂打磨', option_c: '雕刻成型', option_d: '编织收边', answer: 'A', analysis: '点螺以螺钿镶嵌成纹，是漆器装饰工艺。', difficulty: 3 },
  { id: 33, level_id: 4, question_type: 'judge', question_text: '扬州玉雕在清代因盐商经济推动达到鼎盛。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '清代扬州盐商奢靡之风推动玉器业鼎盛。', difficulty: 2 },
  { id: 34, level_id: 4, question_type: 'single', question_text: '扬州刺绣擅长表现的画种风格是？', option_a: '水墨山水', option_b: '油画肖像', option_c: '版画插图', option_d: '壁画飞天', answer: 'A', analysis: '扬州刺绣以针代笔表现水墨画的浓淡干湿。', difficulty: 3 },
  { id: 35, level_id: 4, question_type: 'image', question_text: '下图所示为哪种非遗的创作场景？', option_a: '扬州剪纸', option_b: '玉雕抛光', option_c: '漆器髹涂', option_d: '木偶制作', image: '/static/images/quiz-papercut.jpg', answer: 'A', analysis: '图中为剪纸创作场景，一剪一染见功夫。', difficulty: 2 },
  { id: 36, level_id: 4, question_type: 'single', question_text: '“剪纸绣样”的主要用途是？', option_a: '为刺绣提供底样', option_b: '建筑彩绘打底', option_c: '漆器纹样拓印', option_d: '木雕图样复制', answer: 'A', analysis: '剪纸常用于刺绣底样，是剪纸最早的功能之一。', difficulty: 3 },
  { id: 37, level_id: 4, question_type: 'judge', question_text: '扬州漆器的“平磨螺钿”属于镶嵌类工艺。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '平磨螺钿以螺钿打磨拼嵌成图。', difficulty: 3 },
  { id: 38, level_id: 4, question_type: 'single', question_text: '扬州剪纸从用途上最早多用于？', option_a: '刺绣样稿', option_b: '门窗装饰', option_c: '礼品包装', option_d: '书籍插图', answer: 'A', analysis: '早期剪纸多为刺绣样稿与喜庆装饰。', difficulty: 3 },
  { id: 39, level_id: 4, question_type: 'single', question_text: '下列哪种色彩体系是蓝印花布的典型特征？', option_a: '蓝白两色', option_b: '五彩斑斓', option_c: '金碧辉煌', option_d: '朱红黛绿', answer: 'A', analysis: '蓝印花布以靛蓝染于白布，蓝白相映。', difficulty: 1 },
  { id: 40, level_id: 4, question_type: 'judge', question_text: '扬州剪纸已被列入联合国教科文组织人类非物质文化遗产代表作名录。', option_a: '错误', option_b: '正确', answer: 'A', analysis: '列入人类非遗名录的是“中国剪纸”整体项目，扬州剪纸是其重要组成部分。', difficulty: 3 },
  // 第五关：非遗大师
  { id: 41, level_id: 5, question_type: 'single', question_text: '下列哪一组非遗项目同属扬州“传统美术”类？', option_a: '扬州剪纸、扬州玉雕', option_b: '扬剧、扬州评话', option_c: '富春茶点、蓝印花布', option_d: '高邮民歌、广陵琴派', answer: 'A', analysis: '剪纸与玉雕均为传统美术类。', difficulty: 3 },
  { id: 42, level_id: 5, question_type: 'single', question_text: '扬州漆器“雕漆嵌玉”融合了哪两种工艺？', option_a: '雕漆与玉石镶嵌', option_b: '点螺与戗金', option_c: '平磨与描金', option_d: '剔红与剔犀', answer: 'A', analysis: '雕漆嵌玉以雕漆为地、镶嵌玉石为饰。', difficulty: 3 },
  { id: 43, level_id: 5, question_type: 'judge', question_text: '“扬州三把刀”于2016年列入江苏省级非物质文化遗产名录。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '“三把刀”技艺列入江苏省级名录，属民俗类。', difficulty: 3 },
  { id: 44, level_id: 5, question_type: 'single', question_text: '富春茶点制作技艺中“魁龙珠”茶的窨制原料是？', option_a: '龙井、魁针、珠兰', option_b: '毛尖、茉莉、桂花', option_c: '普洱、玫瑰、陈皮', option_d: '铁观音、菊花、冰糖', answer: 'A', analysis: '魁龙珠取龙井之味、魁针之色、珠兰之香。', difficulty: 3 },
  { id: 45, level_id: 5, question_type: 'single', question_text: '扬州非遗知识图谱中，“传承人”与“非遗项目”之间的关系类型是？', option_a: '传承（INHERITS）', option_b: '归属（BELONGS_TO）', option_c: '盛行于（PREVAILED_IN）', option_d: '关联民俗（ASSOCIATED_WITH）', answer: 'A', analysis: '图谱中 [:INHERITS] 表示传承人对项目的传承关系。', difficulty: 3 },
  { id: 46, level_id: 5, question_type: 'image', question_text: '下图所示为下列哪种非遗项目的代表作品？', option_a: '玉雕山子', option_b: '剪纸', option_c: '漆器', option_d: '刺绣', image: '/static/images/quiz-jade.jpg', answer: 'A', analysis: '图中为玉雕山子，扬州玉雕擅长大型山子雕。', difficulty: 3 },
  { id: 47, level_id: 5, question_type: 'judge', question_text: 'AI 生成的非遗风格作品在平台中会标注“AI创作”标识。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '按平台合规要求，AI 生成内容均标注“AI创作”。', difficulty: 1 },
  { id: 48, level_id: 5, question_type: 'single', question_text: '扫码导览功能中，二维码解析出的关键参数是？', option_a: '项目ID', option_b: '用户ID', option_c: '音频时长', option_d: '地图坐标', answer: 'A', analysis: '二维码内含项目ID，扫码后跳转对应详情与讲解。', difficulty: 2 },
  { id: 49, level_id: 5, question_type: 'single', question_text: '扬州评话在表演中“一人摹拟百样角色”的表现手法称为？', option_a: '演口', option_b: '噱功', option_c: '方口', option_d: '圆口', answer: 'A', analysis: '“演口”指演员以声口、神态摹拟各类角色。', difficulty: 3 },
  { id: 50, level_id: 5, question_type: 'judge', question_text: '平台的知识图谱数据存储于 Neo4j 图数据库中。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '非遗实体与关系存储于 Neo4j，业务数据存储于 MySQL。', difficulty: 2 }
]

/* ---------------- 智能问答 Mock 回复 ---------------- */
export const qaAnswers = [
  {
    keywords: ['剪纸', '历史', '多少年'],
    answer: '扬州剪纸源于唐宋、兴盛于明清，距今已有一千多年历史。清代扬州盐商云集，剪纸广泛应用于刺绣样稿与喜庆装饰，逐渐形成“细、秀、雅、活”的艺术风格。2006年，扬州剪纸列入第一批国家级非物质文化遗产名录。',
    audio: '/static/audio/qa-jianzhi.mp3'
  },
  {
    keywords: ['漆器', '工艺', '多久'],
    answer: '扬州漆器髹饰技艺综合雕漆、点螺、平磨螺钿等“十大工艺”。一件雕漆作品需髹涂数十至数百道大漆，每道漆都要在窨房中阴干，整个制作周期往往需要数月甚至数年。2006年列入第一批国家级非物质文化遗产名录。',
    audio: '/static/audio/qa-qiqi.mp3'
  },
  {
    keywords: ['玉雕', '山子'],
    answer: '扬州玉雕讲究“因料施艺、量材取形”，尤其擅长大型山子雕，将山水人物凝于一玉，被誉为中国玉雕的“南派”代表。清代因盐商经济推动达到鼎盛，“扬州工”由此名扬天下。',
    audio: '/static/audio/qa-yudiao.mp3'
  },
  {
    keywords: ['早茶', '三丁包', '富春'],
    answer: '扬州早茶以富春茶社为代表，“早上皮包水”是扬州人的生活习俗。富春三丁包以鸡丁、肉丁、笋丁为馅，讲究鸡丁大、笋丁脆、肉丁香；佐茶以“魁龙珠”最为经典，取龙井之味、魁针之色、珠兰之香。',
    audio: '/static/audio/qa-fuchun.mp3'
  }
]

export default { categories, projects, inheritors, graphData, gameLevels, questions, qaAnswers }
