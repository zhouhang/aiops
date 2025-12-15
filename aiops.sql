-- 1. 商家表 (t_merchant)
CREATE TABLE `t_merchant` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '商家唯一主键ID',
  `username` varchar(100) NOT NULL DEFAULT '' COMMENT '商家账号',
  `password` varchar(100) NOT NULL DEFAULT '' COMMENT '商家密码',
  `name` varchar(100) NOT NULL DEFAULT '' COMMENT '商家名称',
  `industry` varchar(50) DEFAULT NULL COMMENT '适用行业（如：电商、教育、餐饮）',
  `address` varchar(255) DEFAULT NULL COMMENT '商家地址',
  `manager` varchar(50) DEFAULT NULL COMMENT '负责人姓名',
  `contact` varchar(50) DEFAULT NULL COMMENT '联系电话',
  `sms` varchar(255) DEFAULT NULL COMMENT '短信服务配置/密钥（建议加密存储）',
  `wechat_api` varchar(255) DEFAULT NULL COMMENT '微信API配置/密钥（建议加密存储）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录最后更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_name` (`name`),
  KEY `idx_update_time` (`update_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商家主信息表';

-- 2. 订单表 (t_order) - 用于分析召回用户
CREATE TABLE `t_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `order_id` varchar(64) NOT NULL DEFAULT '' COMMENT '商家原始订单号，唯一标识一笔订单',
  `merchant_id` int(11) NOT NULL COMMENT '关联的商家ID',
  `industry` varchar(50) DEFAULT NULL COMMENT '适用行业（如：电商、教育、餐饮）',
  `user_id` varchar(64) NOT NULL DEFAULT '' COMMENT '用户唯一标识（如手机号、OpenID、商家会员ID）',
  `name` varchar(100) DEFAULT NULL COMMENT '用户姓名（如有）',
  `product` varchar(255) DEFAULT NULL COMMENT '购买的商品或服务名称',
  `product_type` varchar(50) DEFAULT NULL COMMENT '适用商品类型（如：美妆、数码、课程）',
  `contact` varchar(255) DEFAULT NULL COMMENT '用户联系方式（根据contact_type存储对应值，建议加密）',
  `contact_type` varchar(20) DEFAULT NULL COMMENT '联系方式类型：mobile-手机号, wechat_openid-微信OpenID, wechat_unionid-微信UnionID, alipay_userid-支付宝用户ID, email-邮箱, other-其他',
  `amount` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '订单金额',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录最后更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_merchant_order_id` (`merchant_id`, `order_id`) COMMENT '同一商家下的订单号必须唯一',
  KEY `idx_merchant_user` (`merchant_id`, `user_id`) COMMENT '用于快速查询商家的某个用户',
  KEY `idx_merchant_time` (`merchant_id`, `create_time`) COMMENT '用于按商家和时间范围筛选订单',
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户历史订单表';

-- 3. 召回记录表 (t_recall)，Agent在生成召回链接的时候就插入此表
CREATE TABLE `t_recall` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '召回记录主键ID',
  `merchant_id` int(11) NOT NULL COMMENT '关联的商家ID',
  `user_name` varchar(256) NOT NULL DEFAULT '' COMMENT '被召回的用户名称',
  `token` varchar(128) NOT NULL DEFAULT '' COMMENT '唯一访问令牌，用于生成召回链接',
  `token_expired` datetime NOT NULL COMMENT '令牌过期时间',
  `contact` varchar(255) DEFAULT NULL COMMENT '用户联系方式（根据contact_type存储对应值，建议加密）',
  `contact_type` varchar(20) DEFAULT NULL COMMENT '联系方式类型：mobile-手机号, wechat_openid-微信OpenID, wechat_unionid-微信UnionID, alipay_userid-支付宝用户ID, email-邮箱, other-其他',
  `product` varchar(255) DEFAULT NULL COMMENT '购买的商品或服务名称',
  `product_type` varchar(50) DEFAULT NULL COMMENT '产品偏好,适用商品类型（如：美妆、数码、课程）',
  `coupon_type` varchar(20) NOT NULL COMMENT '优惠券类型：full_minus(满减)、no_threshold(无门槛)、free_trial(免费体验)',
  `coupon_value` varchar(100) NOT NULL DEFAULT '' COMMENT '优惠券具体值，如“399-60”或“10”',
  `click` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否点击召回链接：0-否，1-是',
  `claim` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否领取优惠券：0-否，1-是',
  `writeoff` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否已核销：0-否，1-是（手动或自动）',
  `click_time` datetime DEFAULT NULL COMMENT '点击召回链接的时间',
  `claim_time` datetime DEFAULT NULL COMMENT '点击领取的时间',
  `writeoff_time` datetime DEFAULT NULL COMMENT '优惠券核销时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间，即发起召回的时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录最后更新时间',
  PRIMARY KEY (`id`),
  -- >>> 新增唯一索引：确保token唯一且查询高效 <<<
  UNIQUE KEY `uk_token` (`token`),
  -- 为token有效期查询添加索引，便于定时清理过期任务
  KEY `idx_token_expired` (`token_expired`), 
  KEY `idx_merchant_user` (`merchant_id`) COMMENT '用于查询商家对某用户的召回历史',
  KEY `idx_create_time` (`create_time`) COMMENT '用于分析召回活动效果', 
  KEY `idx_writeoff` (`writeoff`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户召回结果记录表';

-- 1. 插入商家测试数据
INSERT INTO `t_merchant` (
  `username`, `password`, `name`, `industry`, `address`, 
  `manager`, `contact`, `sms`, `wechat_api`
) VALUES (
  'test_merchant',
  'hashed_password_123',  -- 实际使用时应该存储加密后的密码
  '测试商家有限公司',
  '电商',
  '北京市朝阳区测试路123号',
  '张经理',
  '13800138000',
  '{"api_key": "sms_test_key", "secret": "sms_test_secret"}',  -- JSON格式存储配置
  '{"app_id": "wx_test_appid", "app_secret": "wx_test_secret"}'  -- JSON格式存储配置
);

-- 2. 插入订单测试数据（关联刚才插入的商家）
INSERT INTO `t_order` (
  `order_id`, `merchant_id`, `industry`, `user_id`, `name`, 
  `product`, `product_type`, `contact`, `contact_type`, `amount`
) VALUES (
  'ORDER_20240115001',
  1,  -- 假设刚才插入的商家ID为1
  '电商',
  'USER_001',
  '张测试',
  'iPhone 15 Pro 256GB',
  '数码',
  '13800138001',  -- 注意：实际生产环境应该加密存储
  'mobile',
  8999.00
);

-- 3. 插入召回记录测试数据
INSERT INTO `t_recall` (
  `merchant_id`, `user_name`, `token`, `token_expired`, 
  `contact`, `contact_type`, `product`, `product_type`, `coupon_type`, `coupon_value`, `click`, `claim`, `writeoff`
) VALUES (
  1,  -- 商家ID
  '张测试',
  '08202fad-d0df-e0b1-0864-141c598c00ecabc123xyz789',
  DATE_ADD(NOW(), INTERVAL 7 DAY),  -- 令牌7天后过期
  '13800138001',
  'mobile',
  '暗区突围',
  '游戏',
  'no_threshold',
  '10',  -- 优惠券面值10元
  0,  -- 未点击
  0,  -- 未领取
  0   -- 未核销
);