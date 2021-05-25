import pymysql
import random
from datetime import datetime
import hashlib

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
        passwd='pass@word',
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
except:
    print("[+] Error: unable to select data")

# TIMESTAMP
timestamp = datetime.now().strftime('%Y%m%d%H%M%S').encode()

# PAGE TITLE
title = 'nowiz'.capitalize()
title = title.encode()

# PAGE CONTENT -> SHA1 -> BASE36 encode
plain_text = "nowiz"    # 평문
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
content_size        = len(old_text)
content_sha1        = base36
content_model       = 1
content_address     = 'tt:{}'.format(page_latest).encode()    # tt:<id> where <id> is old_id -> rev_id -> page_latest

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

try:
    cursor.execute(sql_page, data_page)
    cursor.execute(sql_text, data_text)
    cursor.execute(sql_revision, data_revision)
    cursor.execute(sql_content, data_content)
    print("[+] INSERT QUERY OK")
    db.commit()
except:
    print("[+] Error: unable to insert data")
    db.rollback()

db.close()
