import uuid
import hashlib

# 根据用户输入生成类似 gptkey 的唯一 API 密钥
def generate_api_key(user_id,user_input):
    hashed_input = hashlib.sha256(user_input.encode()).hexdigest()
    return f"sk-{user_id}-{hashed_input}-{uuid.uuid4()}"

# 存储 API 密钥（这里使用一个简单的字典来存储）
api_keys = {}

# 添加 API 密钥到存储
def add_api_key(user_id, user_input):
    api_key = generate_api_key(user_id,user_input)
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    api_keys[user_id] = hashed_key
    return api_key

# 验证 API 密钥
def verify_api_key(user_id, api_key):
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    stored_hashed_key = api_keys.get(user_id)
    return stored_hashed_key == hashed_key


user_id = 'user123'
twitter_handle = 'cigs@cigs'
agent_name = 'cigs_agent'
main_purpose = 'cigs_purpose'
work_description = 'cigs_description'
writing_style = 'cigs_style'
sample_content = 'cigs_content'
common_phrases = 'cigs_phrases'
model_selection = 'cigs_selection'

user_input = f"{twitter_handle}-{agent_name}-{main_purpose}-{work_description}-{writing_style}-{sample_content}-{common_phrases}-{model_selection}"
api_key = add_api_key(user_id, user_input)
print(f"Generated API Key for {user_id}: {api_key}")

is_valid = verify_api_key(user_id, api_key)
print(f"API Key is valid: {is_valid}")

is_valid = verify_api_key(user_id, 'sk-user123-56fdd1a476130a9c820f1ccf0efbe33e1279ae4cb86a756eab32ec55b491483e-495777b9-3cc3-4f3c-8538-6b219c19345e')
print(f"API Key is valid: {is_valid}")