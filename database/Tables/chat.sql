Create TABLE 'repository' (
    'id' INT NOT NULL AUTO_INCREMENT,
    'session_id' INT NOT NULL,
    'role' VARCHAR(20) NOT NULL,
    'content' TEXT NOT NULL,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('session_id') REFERENCES 'session'('id')
) AUTO_INCREMENT=1;