# SG/CW Portal - IIITD
Web Portal for managing Self Growth and Community Work projects for the students of IIIT Delhi, India.

## Installation Setup

### Prerequisites
Here's a list of things you'll need to have prior to setting up the software.
1. Python3
2. MySQL
3. Memcached

### Setup
1. Create a new `SQL` database with the name `cw_portal` and create a new SQL user `cw` with all privileges on `cw_portal` database.

2. Install the required packages
```shell
sudo apt-get install python-dev \
    build-essential libssl-dev libffi-dev \
    libxml2-dev libxslt1-dev zlib1g-dev \
    python-pip
sudo apt-get install libmysqlclient-dev
sudo apt-get install python-mysqldb
pip3 install mysql-python
```

3. Install the required libraries.
```shell
pip3 install requirements.txt
```

4. Setup Migrations
```shell
python3 manage.py migrate
```

5. Setup SQL database variables as follows
```sql
USE cw_portal

INSERT INTO `cw_portal`.`supervisor_flags`
(`name`, `value`)
VALUES
("add_project", 1);

INSERT INTO `cw_portal`.`studentportal_category`
(`name`, `description`)
VALUES
("SG", "Self Growth");

INSERT INTO `cw_portal`.`studentportal_category`
(`name`, `description`)
VALUES
("CW", "Community Work");
```

6. Create a new superuser
```shell
python3 manage.py createsuperuser
```

7. Run your portal
```shell
python3 manage.py runserver
```

8. You can alternatively set up WSGI and NGINX to serve the website.

## Contributors

### Current maintainers 
1. [Chirag Jain](https://github.com/chirag-jn)
2. [Reeshabh Ranjan](https://github.com/reeshabhranjan)

### Old maintainers
1. [Sambhav Satija](https://github.com/darkryder)