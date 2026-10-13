-- =====================================================================
-- Heritouch 地方非遗文化AI解码与传承平台 —— MySQL 数据库结构脚本
-- 版本：v1.0
-- 说明：本脚本与后端 SQLAlchemy 模型（server/app/models/）保持一致，
--       在 MySQL 8.0 上执行，存储引擎 InnoDB，字符集 utf8mb4。
-- 用法：mysql -u root -p < schema.sql   （或由 docker-entrypoint-initdb.d 自动执行）
-- =====================================================================

-- 创建数据库（不存在时才创建），排序规则 utf8mb4_general_ci
CREATE DATABASE IF NOT EXISTS `heritouch`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE `heritouch`;

-- ---------------------------------------------------------------------
-- 1. 非遗项目表：核心内容表，存储非遗项目的全部图文与语音资料
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `heritage_project` (
  `id`              BIGINT       NOT NULL AUTO_INCREMENT            COMMENT '项目ID',
  `name`            VARCHAR(100) NOT NULL                           COMMENT '项目名称',
  `level`           VARCHAR(20)  NOT NULL DEFAULT ''                COMMENT '非遗级别（国家级/省级/市级/县级）',
  `category`        VARCHAR(50)  NOT NULL DEFAULT ''                COMMENT '非遗类别（传统技艺/传统美术/传统戏剧/传统音乐/曲艺/民俗/传统医药）',
  `region`          VARCHAR(50)  NOT NULL DEFAULT ''                COMMENT '申报地区（如 江苏扬州）',
  `batch`           INT          NULL                               COMMENT '列入名录批次年份',
  `intro`           TEXT         NULL                               COMMENT '项目简介',
  `history`         TEXT         NULL                               COMMENT '历史渊源',
  `craft`           TEXT         NULL                               COMMENT '工艺流程/技艺特点',
  `cover_image`     VARCHAR(255) NULL                               COMMENT '封面图URL',
  `audio_mandarin`  VARCHAR(255) NULL                               COMMENT '普通话讲解音频URL',
  `audio_dialect`   VARCHAR(255) NULL                               COMMENT '方言讲解音频URL',
  `qrcode`          VARCHAR(255) NULL                               COMMENT '二维码图片URL（扫码导览用）',
  `latitude`        DECIMAL(10,6) NULL                              COMMENT '纬度（项目所在地大致坐标）',
  `longitude`       DECIMAL(10,6) NULL                              COMMENT '经度（项目所在地大致坐标）',
  `create_time`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_category` (`category`),
  KEY `idx_level` (`level`),
  KEY `idx_region` (`region`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='非遗项目表';

-- ---------------------------------------------------------------------
-- 2. 传承人表：非遗项目代表性传承人信息（演示数据可在后台替换）
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `inheritor` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT            COMMENT '传承人ID',
  `name`        VARCHAR(50)  NOT NULL                           COMMENT '姓名',
  `gender`      CHAR(1)      NULL                               COMMENT '性别（男/女）',
  `project_id`  BIGINT       NOT NULL                           COMMENT '所属非遗项目ID',
  `title`       VARCHAR(50)  NULL                               COMMENT '传承人称号（如 国家级代表性传承人）',
  `biography`   TEXT         NULL                               COMMENT '人物简介（一句话概括）',
  `photo`       VARCHAR(255) NULL                               COMMENT '照片URL',
  `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_project` (`project_id`),
  CONSTRAINT `fk_inheritor_project` FOREIGN KEY (`project_id`) REFERENCES `heritage_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='非遗传承人表';

-- ---------------------------------------------------------------------
-- 3. 系统用户表：微信登录用户，score 为闯关累计积分
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `sys_user` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT            COMMENT '用户ID',
  `openid`      VARCHAR(100) NOT NULL                           COMMENT '微信 openid / 设备唯一标识',
  `nickname`    VARCHAR(50)  NULL                               COMMENT '昵称',
  `avatar`      VARCHAR(255) NULL                               COMMENT '头像URL',
  `score`       INT          NOT NULL DEFAULT 0                 COMMENT '累计积分',
  `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='系统用户表';

-- ---------------------------------------------------------------------
-- 4. 闯关关卡表：科普闯关关卡配置
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `game_level` (
  `id`             BIGINT       NOT NULL AUTO_INCREMENT            COMMENT '关卡ID',
  `name`           VARCHAR(50)  NOT NULL                           COMMENT '关卡名称（如 入门学徒）',
  `subtitle`       VARCHAR(100) NULL                               COMMENT '关卡副标题',
  `rank`           VARCHAR(20)  NULL                               COMMENT '对应段位（学徒/弟子/匠人/大师）',
  `need_score`     INT          NOT NULL DEFAULT 0                 COMMENT '解锁所需累计积分',
  `theme`          VARCHAR(50)  NULL                               COMMENT '关卡主题（如 传统技艺）',
  `question_count` INT          NOT NULL DEFAULT 10                COMMENT '每关题量',
  `icon`           VARCHAR(20)  NULL                               COMMENT '关卡图标（emoji）',
  `sort`           INT          NOT NULL DEFAULT 0                 COMMENT '排序（升序）',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='科普闯关关卡表';

-- ---------------------------------------------------------------------
-- 5. 闯关题目表：单选/判断/识图三类题型，answer 不下发前端
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `game_question` (
  `id`            BIGINT        NOT NULL AUTO_INCREMENT            COMMENT '题目ID',
  `level_id`      BIGINT        NOT NULL                           COMMENT '所属关卡ID',
  `question_type` VARCHAR(20)   NOT NULL DEFAULT 'single'          COMMENT '题型（single 单选/judge 判断/image 识图）',
  `question_text` TEXT          NULL                               COMMENT '题干',
  `option_a`      VARCHAR(255)  NULL                               COMMENT '选项A',
  `option_b`      VARCHAR(255)  NULL                               COMMENT '选项B',
  `option_c`      VARCHAR(255)  NULL                               COMMENT '选项C',
  `option_d`      VARCHAR(255)  NULL                               COMMENT '选项D',
  `answer`        CHAR(1)       NOT NULL                           COMMENT '正确答案（A/B/C/D）',
  `analysis`      TEXT          NULL                               COMMENT '答案解析',
  `image`         VARCHAR(255)  NULL                               COMMENT '识图题图片URL',
  `difficulty`    INT           NOT NULL DEFAULT 1                 COMMENT '难度（1 易/2 中/3 难）',
  `create_time`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_level` (`level_id`),
  CONSTRAINT `fk_question_level` FOREIGN KEY (`level_id`) REFERENCES `game_level` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='闯关题目表';

-- ---------------------------------------------------------------------
-- 6. 闯关记录表：每次通关结算成绩
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `game_record` (
  `id`            BIGINT       NOT NULL AUTO_INCREMENT            COMMENT '记录ID',
  `user_id`       BIGINT       NOT NULL                           COMMENT '用户ID',
  `level_id`      BIGINT       NOT NULL                           COMMENT '关卡ID',
  `score`         INT          NOT NULL DEFAULT 0                 COMMENT '本关得分',
  `total`         INT          NOT NULL DEFAULT 0                 COMMENT '本关满分',
  `correct_count` INT          NOT NULL DEFAULT 0                 COMMENT '答对题数',
  `create_time`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_level_record` (`level_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='闯关成绩记录表';

-- ---------------------------------------------------------------------
-- 7. 用户收藏表：收藏项目/传承人/作品，同一用户同类同目标唯一
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `user_favorite` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT            COMMENT '收藏ID',
  `user_id`     BIGINT       NOT NULL                           COMMENT '用户ID',
  `fav_type`    VARCHAR(20)  NOT NULL DEFAULT 'project'         COMMENT '收藏类型（project 项目/inheritor 传承人/work 作品）',
  `fav_id`      BIGINT       NOT NULL                           COMMENT '收藏目标ID',
  `fav_name`    VARCHAR(100) NULL                               COMMENT '收藏目标名称（冗余存储便于展示）',
  `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_fav` (`user_id`, `fav_type`, `fav_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户收藏表';

-- ---------------------------------------------------------------------
-- 8. 错题本表：闯关答错题目，wrong_count 累计错误次数
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `wrong_question` (
  `id`              BIGINT   NOT NULL AUTO_INCREMENT COMMENT '错题记录ID',
  `user_id`         BIGINT   NOT NULL                COMMENT '用户ID',
  `question_id`     BIGINT   NOT NULL                COMMENT '题目ID',
  `wrong_count`     INT      NOT NULL DEFAULT 1      COMMENT '累计答错次数',
  `last_wrong_time` DATETIME NULL                    COMMENT '最近答错时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_question` (`user_id`, `question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户错题本表';

-- ---------------------------------------------------------------------
-- 9. 用户作品表：AI 互动创作产出的纹样/剧本/画作
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `user_work` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT            COMMENT '作品ID',
  `user_id`     BIGINT       NOT NULL                           COMMENT '作者用户ID',
  `work_type`   VARCHAR(20)  NOT NULL DEFAULT 'pattern'         COMMENT '作品类型（pattern 纹样/script 剧本/painting 画作）',
  `title`       VARCHAR(200) NULL                               COMMENT '作品标题',
  `content`     TEXT         NULL                               COMMENT '作品内容（图片URL或剧本文本）',
  `style`       VARCHAR(50)  NULL                               COMMENT '创作风格（如 扬州剪纸/漆画）',
  `prompt`      TEXT         NULL                               COMMENT '用户输入提示词',
  `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创作时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_work` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户AI作品表';
