import pymysql

### MAIN start
db = pymysql.connect(
        user='wikiuser',
        passwd='nowiz',
        host='localhost',
        db='wikidb',
        charset='utf8'
        )

cursor = db.cursor(pymysql.cursors.DictCursor)

try:
    sql = """DELETE FROM `page`;"""
    cursor.execute(sql)
    sql = """DELETE FROM `text`;"""
    cursor.execute(sql)
    sql = """DELETE FROM `content`;"""
    cursor.execute(sql)
    sql = """DELETE FROM `revision`;"""
    cursor.execute(sql)
    sql = """DELETE FROM `slots`"""
    cursor.execute(sql)
    sql = """DELETE FROM `comment`"""
    cursor.execute(sql)
    sql = """DELETE FROM `revision_comment_temp`"""
    cursor.execute(sql)
    sql = """DELETE FROM `revision_actor_temp`"""
    cursor.execute(sql)
    print("[+] DELETE QUERY OK")

    sql = """ALTER TABLE `page` auto_increment=0;"""
    cursor.execute(sql)
    sql = """ALTER TABLE `text` auto_increment=0;"""
    cursor.execute(sql)
    sql = """ALTER TABLE `content` auto_increment=0;"""
    cursor.execute(sql)
    sql = """ALTER TABLE `revision` auto_increment=0;"""
    cursor.execute(sql)
    sql = """ALTER TABLE `comment` auto_increment=0;"""
    cursor.execute(sql)
    print("[+] ALTER TABLE QUERY OK")

    db.commit()
except:
    print("[+] Error: unable to delete data")
    db.rollback()

db.close()
