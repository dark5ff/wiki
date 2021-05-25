# Mediawiki install
https://www.mediawiki.org/wiki/Special:MyLanguage/Manual:Installation_requirements
## 1. Requirements
```
sudo apt-get install php php-apcu php-intl php-mbstring php-xml php-mysql mariadb-server apache2
```

https://www.mediawiki.org/wiki/Manual:Installing_MediaWiki
## 2. Install
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

https://www.mediawiki.org/wiki/Manual:Config_script
## 4. Configuration
Open your browser and go to:
```
http://localhost/w/mw-config/index.php
```

Follow instructions refer to this link:
https://wnw1005.tistory.com/570
https://wnw1005.tistory.com/571
