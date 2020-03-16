use cw_portal;
CREATE TABLE IF NOT EXISTS auth_user (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	password	varchar(128) NOT NULL,
	last_login	datetime NOT NULL,
	is_superuser	bool NOT NULL,
	username	varchar(30) NOT NULL UNIQUE,
	first_name	varchar(30) NOT NULL,
	last_name	varchar(30) NOT NULL,
	email	varchar(75) NOT NULL,
	is_staff	bool NOT NULL,
	is_active	bool NOT NULL,
	date_joined	datetime NOT NULL
);
CREATE TABLE IF NOT EXISTS studentportal_category (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	name	varchar(300) NOT NULL,
	description	varchar(1000) NOT NULL
);
CREATE TABLE IF NOT EXISTS studentportal_ngo (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	name	varchar(1000) NOT NULL,
	link	varchar(200) NOT NULL,
	details	text NOT NULL,
	category_id	integer,
	FOREIGN KEY(category_id) REFERENCES studentportal_category(id)
);
CREATE TABLE IF NOT EXISTS studentportal_project (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	title	varchar(1000) NOT NULL,
	date_created	datetime NOT NULL,
	credits	integer NOT NULL,
	NGO_name	varchar(1000) NOT NULL,
	NGO_details	varchar(1000) NOT NULL,
	NGO_super	varchar(1000) NOT NULL,
	NGO_super_contact	varchar(100) NOT NULL,
	goals	text NOT NULL,
	schedule_text	text NOT NULL,
	finish_date	datetime,
	stage	integer NOT NULL,
	deleted	bool NOT NULL,
	NGO_id	integer,
	category_id	integer NOT NULL,
	student_id	integer NOT NULL,
	FOREIGN KEY(category_id) REFERENCES studentportal_category(id),
	FOREIGN KEY(NGO_id) REFERENCES studentportal_ngo(id),
	FOREIGN KEY(student_id) REFERENCES auth_user(id)
);
CREATE TABLE IF NOT EXISTS supervisor_example (
	project_id	integer NOT NULL,
	date_created	datetime NOT NULL,
	likes_count	integer NOT NULL,
	comments_count	integer NOT NULL,
	FOREIGN KEY(project_id) REFERENCES studentportal_project(id),
	PRIMARY KEY(project_id)
);
CREATE TABLE IF NOT EXISTS supervisor_comment (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	text	varchar(200) NOT NULL,
	commentor_id	integer NOT NULL,
	project_id	integer NOT NULL,
	FOREIGN KEY(commentor_id) REFERENCES auth_user(id),
	FOREIGN KEY(project_id) REFERENCES supervisor_example(project_id)
);
CREATE TABLE IF NOT EXISTS supervisor_diff (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	diff_type	integer NOT NULL,
	details	text,
	`when`	datetime NOT NULL,
	person_id	integer,
	project_id	integer,
	FOREIGN KEY(person_id) REFERENCES auth_user(id),
	FOREIGN KEY(project_id) REFERENCES studentportal_project(id)
);
CREATE TABLE IF NOT EXISTS supervisor_ta (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	email	varchar(100) NOT NULL,
	instructor	bool NOT NULL
);
CREATE TABLE IF NOT EXISTS supervisor_notification (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	noti_type	integer,
	NGO_name	varchar(200) NOT NULL,
	NGO_link	varchar(200) NOT NULL,
	NGO_details	text NOT NULL,
	NGO_sugg_by_id	integer,
	project_id	integer,
	FOREIGN KEY(NGO_sugg_by_id) REFERENCES auth_user(id),
	FOREIGN KEY(project_id) REFERENCES studentportal_project(id)
);
CREATE TABLE IF NOT EXISTS supervisor_news (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	content	text NOT NULL,
	date_created	datetime NOT NULL,
	priority	bool NOT NULL
);
CREATE TABLE IF NOT EXISTS supervisor_like (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	liked_by_id	integer NOT NULL,
	project_id	integer NOT NULL,
	FOREIGN KEY(project_id) REFERENCES supervisor_example(project_id),
	FOREIGN KEY(liked_by_id) REFERENCES auth_user(id)
);

CREATE TABLE IF NOT EXISTS studentportal_document (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	document	varchar(100) NOT NULL,
	name	varchar(100) NOT NULL,
	date_added	datetime NOT NULL,
	category	integer NOT NULL,
	project_id	integer NOT NULL,
	FOREIGN KEY(project_id) REFERENCES studentportal_project(id)
);

CREATE TABLE IF NOT EXISTS studentportal_feedback (
	project_id	integer NOT NULL,
	hours	integer NOT NULL,
	achievements	text NOT NULL,
	experience	integer NOT NULL,
	FOREIGN KEY(project_id) REFERENCES studentportal_project(id),
	PRIMARY KEY(project_id)
);

CREATE TABLE IF NOT EXISTS studentportal_bug (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	suggestions	text NOT NULL,
	rating	integer NOT NULL,
	user_id	integer,
	FOREIGN KEY(user_id) REFERENCES auth_user(id)
);
CREATE TABLE IF NOT EXISTS socialaccount_socialapp (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	name	varchar(40) NOT NULL,
	client_id	varchar(100) NOT NULL,
	secret	varchar(100) NOT NULL,
	`key`	varchar(100) NOT NULL,
	provider	varchar(30) NOT NULL
);
CREATE TABLE IF NOT EXISTS socialaccount_socialaccount (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	provider	varchar(30) NOT NULL,
	uid	varchar(255) NOT NULL,
	last_login	datetime NOT NULL,
	date_joined	datetime NOT NULL,
	extra_data	text NOT NULL,
	user_id	integer NOT NULL,
	FOREIGN KEY(user_id) REFERENCES auth_user(id),
	UNIQUE(provider,uid)
);
CREATE TABLE IF NOT EXISTS socialaccount_socialtoken (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	token	text NOT NULL,
	token_secret	text NOT NULL,
	expires_at	datetime,
	account_id	integer NOT NULL,
	app_id	integer NOT NULL,
	FOREIGN KEY(account_id) REFERENCES socialaccount_socialaccount(id),
	FOREIGN KEY(app_id) REFERENCES socialaccount_socialapp(id),
	UNIQUE(app_id,account_id)
);
CREATE TABLE IF NOT EXISTS django_site (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	domain	varchar(100) NOT NULL,
	name	varchar(50) NOT NULL
);
CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	socialapp_id	integer NOT NULL,
	site_id	integer NOT NULL,
	UNIQUE(socialapp_id,site_id),
	FOREIGN KEY(site_id) REFERENCES django_site(id),
	FOREIGN KEY(socialapp_id) REFERENCES socialaccount_socialapp(id)
);

CREATE TABLE IF NOT EXISTS django_session (
	session_key	varchar(40) NOT NULL,
	session_data	text NOT NULL,
	expire_date	datetime NOT NULL,
	PRIMARY KEY(session_key)
);
CREATE TABLE IF NOT EXISTS social_auth_nonce (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	server_url	varchar(255) NOT NULL,
	timestamp	integer NOT NULL,
	salt	varchar(65) NOT NULL,
	UNIQUE(server_url,timestamp,salt)
);
CREATE TABLE IF NOT EXISTS social_auth_code (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	email	varchar(75) NOT NULL,
	code	varchar(32) NOT NULL,
	verified	bool NOT NULL,
	UNIQUE(email,code)
);
CREATE TABLE IF NOT EXISTS social_auth_usersocialauth (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	provider	varchar(32) NOT NULL,
	uid	varchar(255) NOT NULL,
	extra_data	text NOT NULL,
	user_id	integer NOT NULL,
	FOREIGN KEY(user_id) REFERENCES auth_user(id),
	UNIQUE(provider,uid)
);
CREATE TABLE IF NOT EXISTS social_auth_association (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	server_url	varchar(255) NOT NULL,
	handle	varchar(255) NOT NULL,
	secret	varchar(255) NOT NULL,
	issued	integer NOT NULL,
	lifetime	integer NOT NULL,
	assoc_type	varchar(64) NOT NULL
);
CREATE TABLE IF NOT EXISTS django_content_type (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	name	varchar(100) NOT NULL,
	app_label	varchar(100) NOT NULL,
	model	varchar(100) NOT NULL,
	UNIQUE(app_label,model)
);
CREATE TABLE IF NOT EXISTS django_admin_log (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	action_time	datetime NOT NULL,
	object_id	text,
	object_repr	varchar(200) NOT NULL,
	action_flag	smallint unsigned NOT NULL,
	change_message	text NOT NULL,
	content_type_id	integer,
	user_id	integer NOT NULL,
	FOREIGN KEY(content_type_id) REFERENCES django_content_type(id),
	FOREIGN KEY(user_id) REFERENCES auth_user(id)
);
CREATE TABLE IF NOT EXISTS account_emailaddress (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	email	varchar(75) NOT NULL UNIQUE,
	verified	bool NOT NULL,
	`primary`	bool NOT NULL,
	user_id	integer NOT NULL,
	FOREIGN KEY(user_id) REFERENCES auth_user(id)
);
CREATE TABLE IF NOT EXISTS account_emailconfirmation (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	created	datetime NOT NULL,
	sent	datetime,
	`key`	varchar(64) NOT NULL UNIQUE,
	email_address_id	integer NOT NULL,
	FOREIGN KEY(email_address_id) REFERENCES account_emailaddress(id)
);

CREATE TABLE IF NOT EXISTS auth_permission (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	name	varchar(50) NOT NULL,
	content_type_id	integer NOT NULL,
	codename	varchar(100) NOT NULL,
	FOREIGN KEY(content_type_id) REFERENCES django_content_type(id),
	UNIQUE(content_type_id,codename)
);
CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	user_id	integer NOT NULL,
	permission_id	integer NOT NULL,
	FOREIGN KEY(permission_id) REFERENCES auth_permission(id),
	FOREIGN KEY(user_id) REFERENCES auth_user(id),
	UNIQUE(user_id,permission_id)
);
CREATE TABLE IF NOT EXISTS auth_group (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	name	varchar(80) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS auth_user_groups (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	user_id	integer NOT NULL,
	group_id	integer NOT NULL,
	FOREIGN KEY(group_id) REFERENCES auth_group(id),
	FOREIGN KEY(user_id) REFERENCES auth_user(id),
	UNIQUE(user_id,group_id)
);

CREATE TABLE IF NOT EXISTS auth_group_permissions (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	group_id	integer NOT NULL,
	permission_id	integer NOT NULL,
	FOREIGN KEY(permission_id) REFERENCES auth_permission(id),
	FOREIGN KEY(group_id) REFERENCES auth_group(id),
	UNIQUE(group_id,permission_id)
);
CREATE TABLE IF NOT EXISTS django_migrations (
	id	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	app	varchar(255) NOT NULL,
	name	varchar(255) NOT NULL,
	applied	datetime NOT NULL
);