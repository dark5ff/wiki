# Mediawiki install
## 1. Requirements
https://www.mediawiki.org/wiki/Special:MyLanguage/Manual:Installation_requirements
```
sudo apt-get install php php-apcu php-intl php-mbstring php-xml php-mysql mysql-server apache2
```

## 2. Install
https://www.mediawiki.org/wiki/Manual:Installing_MediaWiki
```
wget https://releases.wikimedia.org/mediawiki/1.35/mediawiki-1.35.2.tar.gz
tar xvzf mediawiki-*.tar.gz
mv mediawiki-1.35.2/ /var/www/html/w
cd /var/www/html/w/
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
```

## 3. Create Database
### MySQL
```
CREATE DATABASE wikidb;
CREATE USER 'wikiuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON wikidb.* TO 'wikiuser'@'localhost' WITH GRANT OPTION;
```

## 4. Configuration
https://www.mediawiki.org/wiki/Manual:Config_script \
Open your browser and go to:
```
http://localhost/w/mw-config/index.php
```

Follow instructions refer to this link: \
https://wnw1005.tistory.com/570 \
https://wnw1005.tistory.com/571

</hr>

# wiki_insert.py
## 1. Usage
```
root@ubuntu:/home/nowiz/wiki# python3 wiki_insert.py 
[+] Usage: wiki_insert.py [TITLE] [TEXT]
```

## 2. Execute
```
root@ubuntu:/home/nowiz/wiki# python3 wiki_insert.py "Hello World!" "hello world!"
[+] Error: unable to select data
'NoneType' object has no attribute 'items'
Plain text: hello world!
SHA1 hash: 430ce34d020724ed75a196dfc2ad67c77772d169
Base36 encoded text: b'7tykfjd4p27h5228vo2d2p5r7zesns9'
Datas to insert into page:  (0, b'Hello_world!', 0, 1, 0.96581737749, b'20210525005446', b'20210525005446', 1, 12, b'wikitext')
Datas to insert into text:  (b'hello world!', b'utf-8')
Datas to insert into revision:  (1, 0, 0, b'20210525005446', 0, 0, 12, 0, b'7tykfjd4p27h5228vo2d2p5r7zesns9')
Datas to insert into content:  (12, b'7tykfjd4p27h5228vo2d2p5r7zesns9', 1, b'tt:1')
Datas to insert into slots:  (1, 1, 1, 1)
Datas to insert into comment:  (0, b'')
Datas to insert into revision_comment_temp:  (1, 1)
Datas to insert into revision_actor_temp:  (1, 1, b'20210525005446', 1)
[+] INSERT QUERY OK
[+] Success: POST Response 200: 
{"batchcomplete":"","warnings":{"main":{"*":"A POST request was made without a \"Content-Type\" header. This does not work reliably.\nSubscribe to the mediawiki-api-announce mailing list at <https://lists.wikimedia.org/mailman/listinfo/mediawiki-api-announce> for notice of API deprecations and breaking changes."}},"purge":[{"ns":0,"title":"Hello World!","missing":""}]}
```

## 3. Check created page
![image](https://user-images.githubusercontent.com/66773292/119460151-5c2bd100-bd79-11eb-9832-8afc367be6c2.png)
![image](https://user-images.githubusercontent.com/66773292/119460790-00157c80-bd7a-11eb-8d02-f2fa7344242d.png)
