Create TABLE 'repository' (
    'id' INT NOT NULL AUTO_INCREMENT,
    'session_id' INT NOT NULL,
    'name' VARCHAR(255) NOT NULL,
    'repository_id' VARCHAR(255) NOT NULL,
    'url' VARCHAR(255) NOT NULL,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('session_id') REFERENCES 'session'('id')
) AUTO_INCREMENT=1;