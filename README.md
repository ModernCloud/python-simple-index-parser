PyPI XMLRPC search will be permanently [disabled](https://status.python.org/incidents/grk0k7sz6zkp). This project uses [Simple Repository API](https://www.python.org/dev/peps/pep-0503/) to fetch packages and versions. You can follow the instructions to create package_version.sql file.

You can run following commands to create SQL file.
```bash
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python main.py
```

package_version.sql file is working with following schema:

```sql
CREATE TABLE IF NOT EXISTS `python_package` (
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    INDEX name_idx (name),
    UNIQUE KEY version_uniq(name, version)
) DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ENGINE = InnoDB;
```
