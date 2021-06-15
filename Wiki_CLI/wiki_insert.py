# Developed in Python 3.8.5 by Nowiz (giwon9977@naver.com)
import pymysql
import random
from datetime import datetime
import hashlib
import requests
import sys

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

def connect_db():    
    db = pymysql.connect(
             user='root', 
             passwd='intadd', 
             host='127.0.0.1', 
             db='wikidb', 
             charset='utf8'
        )

    return db

def fetch_pageId(cursor):
    # Fetch last row from page table
    sql = """SELECT * FROM `page` ORDER BY `page_id` DESC LIMIT 1;"""

    page_id = 0
    #page_latest = 0

    try:
        cursor.execute(sql)
        result = cursor.fetchone()    # result = dict{col_name0 : value0, col_name1 : value1, ...}

        for key, value in result.items():
            if(key == "page_id"):
                page_id = value
            #if(key == "page_latest"):
                #page_latest = value
        print("[+] SELECT QUERY OK")
    except Exception as e:
        print("[+] Error: unable to select data")
        print(e)

    return page_id

def purgePage(title):
    # Refresh current page (Purge the cache)
    S = requests.Session()

    URL = "http://localhost/w/api.php"

    PARAMS = {
        "action": "purge",
        "titles": title,                    # To purge multiple pages: "titles": "TitleA | TitleB | ..."
        "format": "json"
    }

    try:
        R = S.post(url=URL, params=PARAMS)      # http://localhost/w/api.php?action=purge&titles
        DATA = R.text
        if(R.status_code == 200):
            print(f"[+] Success: POST Response {R.status_code}: ")
        else:
            print(f"[+] Failed: POST Response {R.status_code}: ")
        print(DATA)
    except Exception as e:
        print("[+] Error: unable to send request")
        print(e)
        return -1

    return R.status_code

def init_values(page_id, title, text):
    # TIMESTAMP
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S').encode()

    # PAGE TITLE
    title = title.capitalize()
    title = title.replace(' ', '_')     # Blank in the title replaced with '_'
    title = title.encode()

    # PAGE CONTENT -> SHA1 -> BASE36 encode
    plain_text = text    # 평문
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
    # comment_id        = auto_increment
    comment_hash        = 0                 # type:int
    comment_text        = ''.encode()       # type:blob
    # comment_data      = NULL

    # revision_comment_temp table values
    revcomment_rev          = page_latest   # type:int
    revcomment_comment_id   = page_latest   # type:bigint

    # revision_actor_temp table values
    revactor_rev        = page_latest       # type:int
    revactor_actor      = 1                 # type:bigint / 1:Wikiadmin, 2:Mediawiki default / refer to actor table.
    revactor_timestamp  = timestamp         # type:binary
    revactor_page       = page_latest       # type:int

    # Init set of data
    dataset = []

    # Page data form
    data_page = (
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

    print("Datas to insert into page: ", data_page)
    dataset.append(data_page)

    # Text data form
    data_text = (
            old_text, 
            old_flags
            )

    print("Datas to insert into text: ", data_text)
    dataset.append(data_text)

    # Revision data form
    data_revision = (
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

    print("Datas to insert into revision: ", data_revision)
    dataset.append(data_revision)
    
    # Content data form
    data_content = (
            content_size,
            content_sha1,
            content_model,
            content_address
            )

    print("Datas to insert into content: ", data_content)
    dataset.append(data_content)
    
    # Slots data form
    data_slots = (
            slot_revision_id,
            slot_role_id,
            slot_content_id,
            slot_origin
            )

    print("Datas to insert into slots: ", data_slots)
    dataset.append(data_slots)

    # Comment data form
    data_comment = (
            comment_hash, 
            comment_text
            )

    print("Datas to insert into comment: ", data_comment)
    dataset.append(data_comment)

    # Revision_comment_temp data form
    data_revision_comment_temp = (
            revcomment_rev, 
            revcomment_comment_id
            )

    print("Datas to insert into revision_comment_temp: ", data_revision_comment_temp)
    dataset.append(data_revision_comment_temp)

    # Revision_actor_temp data form
    data_revision_actor_temp = (
            revactor_rev,
            revactor_actor,
            revactor_timestamp,
            revactor_page
            )

    print("Datas to insert into revision_actor_temp: ", data_revision_actor_temp)
    dataset.append(data_revision_actor_temp)

    return dataset


def init_sql():
    # Init set of sql
    sqlset = []

    # SQL Query to execute in page table
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

    sql_text = """INSERT INTO `text` (
            old_text,
            old_flags
        )
        VALUES (
            %s,
            %s
        )"""

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

    sql_comment = """INSERT INTO `comment` (
            comment_hash,
            comment_text)
        VALUES (
            %s,
            %s
        )"""
    sql_revision_comment_temp = """INSERT INTO `revision_comment_temp` (
            revcomment_rev,
            revcomment_comment_id)
        VALUES (
            %s,
            %s
        )"""
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

    # Append SQLs in sqlset
    sqlset.append(sql_page)
    sqlset.append(sql_text)
    sqlset.append(sql_revision)
    sqlset.append(sql_content)
    sqlset.append(sql_slots)
    sqlset.append(sql_comment)
    sqlset.append(sql_revision_comment_temp)
    sqlset.append(sql_revision_actor_temp)

    return sqlset

# Main function
def main():
    # Print usage
    if(len(sys.argv) != 3):
        print(f"[+] Usage: {sys.argv[0]} [TITLE] [TEXT]")
        return -1

    # Get title and text from arguments
    title = sys.argv[1]
    text = sys.argv[2]

    # DB connection and cursor handling
    db = connect_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    page_id = fetch_pageId(cursor)
    dataset = init_values(page_id, title, text)     # dataset = [(tuple1), (tuple2) ... ]
    sqlset = init_sql()                             # sqlset = [(tuple1), (tuple2) ... ]

    try:
        # Execute SQL Query
        for sql, data in zip(sqlset, dataset):
            cursor.execute(sql, data)
        #cursor.execute(sql_page, data_page)
        #cursor.execute(sql_text, data_text)
        #cursor.execute(sql_revision, data_revision)
        #cursor.execute(sql_content, data_content)
        #cursor.execute(sql_slots, data_slots)
        #cursor.execute(sql_comment, data_comment)
        #cursor.execute(sql_revision_comment_temp, data_revision_comment_temp)
        #cursor.execute(sql_revision_actor_temp, data_revision_actor_temp)
        result = cursor.fetchall()
        print(result)
 
        print("[+] INSERT QUERY OK")
        db.commit()
        purgePage(title)
    except Exception as e:
        print("[+] Error: unable to insert data")
        print(e)
        db.rollback()

    db.close()


### MAIN START
if __name__ == '__main__':
    # Call main function
    main()
