# main.py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Dict
from dotenv import load_dotenv
from services.order_service import OrderService
from services.merchant_service import MerchantService
from services.recall_service import RecallService
from datetime import datetime, timezone, timedelta
import uuid, hashlib

# 加载 .env
load_dotenv()

# 初始化 FastAPI
app = FastAPI(title="用户召回 Agent")

# 挂载静态文件（可选）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板目录
templates = Jinja2Templates(directory="templates")

#初始化service对象
merchantService = MerchantService()
orderService = OrderService()
recallService = RecallService()

# === 1. API 接口：登录接口 ===
@app.post("/login")
async def login(request: Request) -> Dict:
    body = await request.json()
    username = body.get("username", None)
    password = body.get("password", None)
    if username is None:
        return {"status_code": "500", "message": "请填写用户名"}
    user = merchantService.get_merchant_by_username(username)
    # 检查用户是否存在
    if user is None:
        return {"status_code": "500", "message": "用户不存在"}
    # 进行用户名密码校验
    if user.get('password') != hashlib.sha256(f"{password}".encode()).hexdigest():
        return {"status_code": "500", "message": "密码不正确"}
    name = user.get('name', username)
    token = hashlib.sha256(f"{username}{password}{datetime.now().timestamp()}".encode()).hexdigest()
    #将token存储n天，避免下次还要登录

    return {
        "status_code": "200",
        "username":username,
        "name":name,
        "token":token,
        "message": "登录成功"
    }

# === 2. API 接口：保存订单 ===
@app.post("/orders/create")
async def create_orders(request: Request):
    body = await request.json()
    orders = body.get("orders", [])
    if not orders:
        return {"status_code": "500", "message": "没有订单数据"}
    # 保存订单数据到数据库
    return orderService.create_orders(orders)

# === 3. API 接口：进行召回用户触达，MVP阶段使用短信或企业微信 ===
@app.post("/recalls/create")
async def create_recalls(request: Request):
    body = await request.json()
    recall_users = body.get("recall_users", [])
    recall_records = []
    for recall_user in recall_users:
        recall_record = {}
        recall_record["merchant_id"] = recall_user.get("merchant_id")
        recall_record["user_name"] = recall_user.get("user_name")
        recall_record["token"] = uuid.uuid4().hex
        recall_record["token_expired"] = datetime.now(timezone.utc) + timedelta(days=7)
        recall_record["product"] = recall_user.get("product")
        recall_record["product_type"] = recall_user.get("product_type")
        recall_record["contact"] = recall_user.get("contact")
        recall_record["contact_type"] = recall_user.get("contact_type")
        recall_records.append(recall_record)
    #insertBatch t_recall记录，作为召回任务发出的记录
    return recallService.create_recalls(recall_records)

# === 4. H5 召回落地页 ===
@app.get("/landing/{token}")
async def recall_landing(request: Request, token: str):
    # TODO: 根据 token 查询用户和优惠券
    recall = recallService.get_recall(token)
    if recall is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": "无效的优惠券链接或优惠券已过期。"
            }
        )
    # 召回触达标记用户已打开
    recallService.recall_click(token)
    id = recall.get("id")
    user_name = recall.get("user_name", "尊敬的用户") if recall else "尊敬的用户"
    product = recall.get("product")
    product_type = recall.get("product_type")
    coupon_value = recall.get("coupon_value")
    coupon_type = recall.get("coupon_type")
    # 处理token_expired，可能是datetime对象或字符串
    token_expired_raw = recall.get("token_expired")
    if isinstance(token_expired_raw, str):
        try:
            token_expired = datetime.strptime(token_expired_raw, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                token_expired = datetime.fromisoformat(token_expired_raw.replace('Z', '+00:00'))
            except ValueError:
                token_expired = datetime.now(timezone.utc) + timedelta(days=7)
    elif isinstance(token_expired_raw, datetime):
        token_expired = token_expired_raw
    else:
        token_expired = datetime.now(timezone.utc) + timedelta(days=7)
    now = datetime.now(timezone.utc) if token_expired.tzinfo else datetime.now()
    token_time_left = (token_expired - now).total_seconds()
    token_time_left = max(0, int(token_time_left))  # 防止负数

    if coupon_value is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": "无效的优惠券链接或优惠券已过期。"
            }
        )
    #解析优惠券展示
    coupon = ""
    if coupon_type == "full_minus":
        try:
            threshold, amount = coupon_value.split("-")
            coupon = f"满{threshold}元立减{amount}元优惠券"
        except (ValueError, AttributeError):
            coupon = f"满额立减优惠券"
    
    if coupon_type == "no_threshold":
        coupon = f"立减{coupon_value}元优惠券"
    
    if coupon_type == "free_trial":
        coupon = f"免费试用{coupon_value}天优惠券"
    

    return templates.TemplateResponse(
        "landing.html",
        {
            "request": request,
            "id": id,
            "user_name": user_name,
            "coupon": coupon,
            "product": product,
            "product_type": product_type,
            "token": token,
            "token_expired": token_expired,
            "token_time_left": token_time_left
        }
    )

# === 5. 打开召回落地页后点击领取 ===
@app.post("/coupon/get")
async def get_coupon(request: Request) -> Dict:
    body = await request.json()
    token = body.get("token", None)
    user_name = body.get("username", None)
    if not token:
        return {"status_code": "500", "message": "token不能为空"}
    recall = recallService.get_recall(token)
    if recall is None:
        return {"status_code": "500", "message": "无效的优惠券链接"}
    click = recall.get("click", 0)
    if click != 1:
        return {"status_code": "500", "message": "请先打开优惠券链接！"}
    recall_user_name = recall.get("user_name")
    if user_name != recall_user_name:
        return {"status_code": "500", "message": "这不是你的优惠券！"}
    #召回触达标记用户已领取优惠
    recallService.recall_claim(token)
    return {"status_code": "200", "message": "优惠券领取成功！请前往游戏内商城使用。"}
    
    