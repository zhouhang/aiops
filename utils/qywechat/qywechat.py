from typing import Dict, List
from wechatpy.enterprise import WeChatClient
from dotenv import load_dotenv
import os
# 加载 .env（只在应用启动时调用一次）
load_dotenv()

class WeChatRecallSender:
    def __init__(self, corp_id: str, secret: str):
        corp_id = os.getenv("WECHAT_CORP_ID")
        secret = os.getenv("WECHAT_SECRET")
        self.client = WeChatClient(corp_id, secret)
    
    # 获取部门下的成员列表
    def get_users(self, department_id : int) -> List[Dict]:
        users = self.client.department.get_users(department_id)
        for user in users['userlist']:
            print(user)
        return users

        # 2. 根据手机号获取userid（需要通讯录同步权限）
        # 注意：这需要通讯录API的读取权限
        # try:
        #     user_info = client.user.get_user_id('13812345678')  # 员工手机号
        #     print(f"userid: {user_info['userid']}")
        #     return users
        # except:
        #     print("未找到该员工或没有权限")
        #     return [{

        #     }]

    # 获取某个员工添加的所有客户列表,批量获取（企业微信限制每次最多100条）
    def get_external_users(self, staff_userid : str):
        external_contacts = []
        cursor = ''  # 用于分页
        while True:
            result = self.client.external_contact.list(
                userid=staff_userid,
                limit=100,
                cursor=cursor
            )
            for ext_id in result['external_userid']:
                print(f"客户ID: {ext_id}")
                external_contacts.append(ext_id)
            
            if not result.get('next_cursor'):
                break
            cursor = result['next_cursor']
        return external_contacts

    def send_recall_message(self, strategy_data):
        """发送召回消息"""
        try:
            # 从策略数据中提取参数
            userid = strategy_data['sender_userid']  # 发送员工ID
            external_userid = strategy_data['external_userid']  # 客户ID
            message_content = strategy_data['personalized_copy']['body']
            
            # 发送文本消息
            result = self.client.external_contact.message.send(
                sender=userid,
                external_user_id=[external_userid],
                msgtype='text',
                text={'content': message_content}
            )
            
            print(f"消息发送成功: {result}")
            return True
            
        except Exception as e:
            print(f"发送失败: {str(e)}")
            return False

# 使用示例
if __name__ == '__main__':
    # 1. 初始化
    sender = WeChatRecallSender(
        corp_id='你的企业ID',
        secret='你的应用Secret'
    )
    
    # 2. 准备数据（这里是你之前生成的召回策略）
    recall_strategy = {
        "merchant_id": 1,
        "user_id": "13812345678",
        "user_name": "张伟",
        "contact": "13812345678",
        "contact_type": "mobile",
        "recall_strategy": {
            "strategy_name": "高价值用户专属回归关怀计划",
            "touch_channel": ["qwx"],
            "personalized_copy": {
                "body": "张伟先生您好，这是您的专属优惠..."
            }
        }
    }
    
    # 3. 需要额外添加的字段（在实际应用中从数据库获取）
    recall_strategy['sender_userid'] = 'zhangsan'  # 谁发送（员工ID）
    recall_strategy['external_userid'] = 'woAJdGCgAXXXXXXXXXX'  # 客户的external_userid
    
    # 4. 发送
    sender.send_recall_message(recall_strategy)