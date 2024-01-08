import uuid
import redis
import asyncio
import logging

from .celery import app
from common.aws import AWSManager
from character.models import Submit
from api.api import upload_img_to_s3
from api.imageGenAPI import ImageGenAPI

MAX_CONCURRENT_REQUESTS = 3

redis_client = redis.StrictRedis(host="redis", port=6379, db=2)

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


# ## 아직 작업 중 시작
def get_ImageCreator_Cookie():
    try:
        cookie = []
        for i in range(2):
            cookie_key = "cookie" + str(i + 1)
            cookie.append(AWSManager.get_secret("BingImageCreator")[cookie_key])
        return cookie
    except Exception as e:
        raise Exception("BingImageCreator API 키를 가져오는 데 실패했습니다.") from e


auth_cookies = get_ImageCreator_Cookie()
print("auth_cookies", *auth_cookies)
# ## 아직 작업 중 끝

app.conf.update({"worker_concurrency": MAX_CONCURRENT_REQUESTS * len(auth_cookies)})


def get_round_robin_key():
    cookie_index = redis_client.incr("cookie_index")
    cookie_index %= len(auth_cookies)
    return cookie_index, auth_cookies[cookie_index]


async def create_image(key, auth_cookie, prompt):
    while True:
        current_requests = redis_client.incr(key)
        if current_requests <= MAX_CONCURRENT_REQUESTS:
            redis_client.delete(key + ":lock")  # 락 해제
            print("get request approval " + str(current_requests))
            print("delete lock " + key + ":lock")
            break
        else:
            redis_client.decr(key)
            await asyncio.sleep(1)

    try:
        image_generator = ImageGenAPI(auth_cookie)
        result = await image_generator.get_images(prompt)
        return result
    except Exception as e:
        raise e
    finally:
        redis_client.decr(key)


@app.task(bind=True)
def create_character(self, submit_id, keywords, duplicate=False):
    cookie_index, auth_cookie = get_round_robin_key()

    key = "concurrent_requests_" + str(cookie_index)

    lock_acquired = False

    try:
        logger.info(keywords)

        # prompt = f'{keywords[3]}에서 {keywords[1]}착용하고 {keywords[2]}들고있는 "{keywords[5]}" 스타일 {keywords[4]} {keywords[0]} character'
        # prompt = f'{keywords[3]}에서 {keywords[1]}착용하고 {keywords[2]}들고있는 "{keywords[5]}" 스타일 {keywords[4]} {keywords[0]} 캐릭터'
        prompt = f"{keywords[3]}에서 {keywords[1]}착용하고 {keywords[2]}들고있는 {keywords[5]} 스타일 {keywords[4]} {keywords[0]} 캐릭터"
        # prompt = f"{keywords[3]}에서 {keywords[1]}착용하고 {keywords[2]}들고있는 {keywords[5]} 스타일 {keywords[4]} {keywords[0]} non-human 캐릭터"

        # prompt = "학교에서 가방착용하고 맥북들고있는 디즈니 스타일 빨간색 햄스터 캐릭터"
        # prompt = "학교에서  안경착용하고 맥북 타이핑 거북이 디즈니 스타일  non human 캐릭터"
        # prompt = "학교에서 안경착용하고 맥북들고있는 거북이 디즈니 스타일 non human 캐릭터"

        logger.info(prompt)

        lock_owner = str(uuid.uuid4())

        while not lock_acquired:
            lock_acquired = redis_client.setnx(key + ":lock", lock_owner)  # 락 설정
            if lock_acquired:
                redis_client.expire(key + ":lock", 16)  # 락의 자동 만료 설정
                print("get lock " + key + ":lock " + lock_owner)
                logger.info("get lock " + key + ":lock " + lock_owner)

        loop = asyncio.get_event_loop()
        result_url, _ = loop.run_until_complete(create_image(key, auth_cookie, prompt))

        if duplicate:
            result_url = upload_img_to_s3(result_url[0])

            submit = Submit.objects.get(id=submit_id)
            submit.result_url = result_url
            submit.save()

        return {"result_url": result_url, "submit_id": submit_id, "keyword": keywords}
    except Exception as e:
        self.update_state(state="FAILURE")

        raise ValueError("Some condition is not met. " + str(e))
    finally:
        if redis_client.get(key + ":lock") == lock_owner:
            redis_client.delete(key + ":lock")  # 락 해제
            print("delete lock " + key + ":lock " + lock_owner)
