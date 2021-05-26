import pymysql
import random
from datetime import datetime
import hashlib
import requests

### Function Defintion
def base36encode(number, alphabet='0123456789abcdefghijklmnopqrstuvwxyz'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36


### MAIN start
db = pymysql.connect(
        user='wikiuser',
        passwd='nowiz',
        host='localhost',
        db='wikidb',
        charset='utf8'
        )

cursor = db.cursor(pymysql.cursors.DictCursor)

# Fetch last row from page table
sql = """SELECT * FROM `page` ORDER BY `page_id` DESC LIMIT 1;"""

page_id = 0
page_latest = 0

try:
    cursor.execute(sql)
    result = cursor.fetchone()  # result = dict{col_name0 : value0, col_name1 : value1, ...}

    for key, value in result.items():
        if(key == "page_id"):
            page_id = value
        if(key == "page_latest"):
            page_latest = value

    print("[+] SELECT QUERY OK")
except Exception as e:
    print("[+] Error: unable to select data")
    print(e)

# TIMESTAMP
timestamp = datetime.now().strftime('%Y%m%d%H%M%S').encode()

# PAGE TITLE
title = 'html'.capitalize()
title = title.replace(' ', '_')     # Blank in the title replaced with '_'
title = title.encode()

# PAGE CONTENT -> SHA1 -> BASE36 encode
plain_text = "<h1> hello world! </h1>"    # 평문
print("Plain text: {}".format(plain_text))

h = hashlib.sha1()
h.update(plain_text.encode('utf-8'))
sha1 = h.hexdigest()    # str
print("SHA1 hash: {}".format(sha1))
sha1 = int(sha1, 16)    # int

base36 = base36encode(sha1)
base36 = base36.encode()
print("Base36 encoded text: {}".format(base36))

# text table values
old_text            = plain_text.encode()
old_flags           = b'utf-8'

# page table values
# page_id           = auto_increment
page_namespace      = 0
page_title          = title
page_is_redirect    = 0
page_is_new         = 1
page_random         = round(random.random(), 12)
page_touched        = timestamp
page_links_updated  = timestamp
page_latest         = page_id + 1
page_len            = len(old_text)
page_content_model  = b'wikitext'

# revision table values
# rev_id            = auto_increment
rev_page            = page_latest
rev_comment_id      = 0
rev_actor           = 0
rev_timestamp       = timestamp
rev_minor_edit      = 0
rev_deleted         = 0
rev_len             = len(old_text)
rev_parent_id       = 0
rev_sha1            = base36

# content table values
# content_id        = auto_increment
content_size        = len(old_text)
content_sha1        = base36
content_model       = 1
content_address     = 'tt:{}'.format(page_latest).encode()    # tt:<id> where <id> is old_id -> rev_id -> page_latest

# slots table values
slot_revision_id    = page_latest       # Originally, rev_id is the right value to slot_revision_id
slot_role_id        = 1                 # role:1 -> main
slot_content_id     = page_latest       # Originally, content_id is the right value to slot_content_id
slot_origin         = page_latest       # Originally, rev_id is the right value to slot_origin

# comment table values
comment_hash        = 0                 # type:int
comment_text        = ''.encode()       # type:blob

# revision_comment_temp table values
revcomment_rev          = page_latest   # type:int
revcomment_comment_id   = page_latest   # type:bigint

# revision_actor_temp table values
revactor_rev        = page_latest       # type:int
revactor_actor      = 1                 # type:bigint / 1:Wikiadmin, 2:Mediawiki default / refer to actor table.
revactor_timestamp  = timestamp         # type:binary
revactor_page       = page_latest       # type:int

# execute page data form
data_page = (page_namespace,
        page_title,
        page_is_redirect,
        page_is_new,
        page_random,
        page_touched,
        page_links_updated,
        page_latest,
        page_len,
        page_content_model)

print("Datas to insert into page: ", data_page)

sql_page = """INSERT INTO `page` (
        page_namespace,
        page_title,
        page_is_redirect,
        page_is_new,
        page_random,
        page_touched,
        page_links_updated,
        page_latest,
        page_len,
        page_content_model
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )"""

# execute text data form
data_text = (old_text,
        old_flags)

print("Datas to insert into text: ", data_text)

sql_text = """INSERT INTO `text` (
        old_text,
        old_flags
    )
    VALUES (
        %s,
        %s
    )"""

# execute revision data form
data_revision = (rev_page,
        rev_comment_id,
        rev_actor,
        rev_timestamp,
        rev_minor_edit,
        rev_deleted,
        rev_len,
        rev_parent_id,
        rev_sha1)

print("Datas to insert into revision: ", data_revision)

sql_revision = """INSERT INTO `revision` (
        rev_page,
        rev_comment_id,
        rev_actor,
        rev_timestamp,
        rev_minor_edit,
        rev_deleted,
        rev_len,
        rev_parent_id,
        rev_sha1
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )"""

# execute content data form
data_content = (content_size,
        content_sha1,
        content_model,
        content_address)

print("Datas to insert into content: ", data_content)

sql_content = """INSERT INTO `content` (
        content_size,
        content_sha1,
        content_model,
        content_address
    )
    VALUES (
        %s,
        %s,
        %s,
        %s
    )"""

# execute slots data form
data_slots = (slot_revision_id,
        slot_role_id,
        slot_content_id,
        slot_origin)

print("Datas to insert into slots: ", data_slots)

sql_slots = """INSERT INTO `slots` (
        slot_revision_id,
        slot_role_id,
        slot_content_id,
        slot_origin)
    VALUES (
        %s,
        %s,
        %s,
        %s
    )"""

# execute comment data form
data_comment = (comment_hash, comment_text)

print("Datas to insert into comment: ", data_comment)

sql_comment = """INSERT INTO `comment` (
        comment_hash,
        comment_text)
    VALUES (
        %s,
        %s
    )"""

# execute revision_comment_temp data form
data_revision_comment_temp = (revcomment_rev, revcomment_comment_id)

print("Datas to insert into revision_comment_temp: ", data_revision_comment_temp)

sql_revision_comment_temp = """INSERT INTO `revision_comment_temp` (
        revcomment_rev,
        revcomment_comment_id)
    VALUES (
        %s,
        %s
    )"""

# execute revision_actor_temp data form
data_revision_actor_temp = (revactor_rev,
        revactor_actor,
        revactor_timestamp,
        revactor_page)

print("Datas to insert into revision_actor_temp: ", data_revision_actor_temp)

sql_revision_actor_temp = """INSERT INTO `revision_actor_temp` (
        revactor_rev,
        revactor_actor,
        revactor_timestamp,
        revactor_page)
    VALUES (
        %s,
        %s,
        %s,
        %s
    )"""

try:
    cursor.execute(sql_page, data_page)
    cursor.execute(sql_text, data_text)
    cursor.execute(sql_revision, data_revision)
    cursor.execute(sql_content, data_content)
    cursor.execute(sql_slots, data_slots)
    cursor.execute(sql_comment, data_comment)
    cursor.execute(sql_revision_comment_temp, data_revision_comment_temp)
    cursor.execute(sql_revision_actor_temp, data_revision_actor_temp)
    print("[+] INSERT QUERY OK")
    db.commit()
except Exception as e:
    print("[+] Error: unable to insert data")
    print(e)
    db.rollback()

db.close()

# Refresh current page (Purge the cache)
S = requests.Session()

URL = "http://localhost/w/api.php"

PARAMS = {
    "action": "purge",
    "titles": title,                    # To purge multiple pages: "titles": "TitleA | TitleB | ..."
    "format": "json"
}

R = S.post(url=URL, params=PARAMS)      # http://localhost/w/api.php?action=purge&titles
DATA = R.text

print("[+] POST Response: ")
print(DATA)
