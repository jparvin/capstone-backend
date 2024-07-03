Create TABLE 'session' (
    'id' INT NOT NULL AUTO_INCREMENT,
    'user_id' INT NOT NULL,
    'name' VARCHAR(255) NOT NULL,
    'organization' VARCHAR(255) NULL,
    'project' VARCHAR(255) NULL,
    'project_name' VARCHAR(255) NULL,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('user_id') REFERENCES 'user'('id')
) AUTO_INCREMENT=1;