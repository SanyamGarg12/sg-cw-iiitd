use cw_portal;

create table if not exists studentportal_bug
(
  id          int auto_increment primary key,
  suggestions text not null,
  rating      int  not null,
  user_id     int  null
);

create index user_id
  on studentportal_bug (user_id);

create table if not exists studentportal_category
(
  id          int auto_increment primary key,
  name        varchar(300) default ''  not null,
  description varchar(1000) default '' not null
);

create table if not exists studentportal_ngo
(
  id          int auto_increment primary key,
  name        varchar(1000) not null,
  link        varchar(200)  not null,
  details     text          not null,
  category_id int           null,
  constraint studentportal_ngo_ibfk_1
  foreign key (category_id) references studentportal_category (id)
);

create index category_id
  on studentportal_ngo (category_id);

create table if not exists studentportal_project
(
  id                int auto_increment primary key,
  title             varchar(1000) not null,
  date_created      datetime      not null,
  credits           int           not null,
  NGO_name          varchar(1000) not null,
  NGO_details       varchar(1000) not null,
  NGO_super         varchar(1000) not null,
  NGO_super_contact varchar(100)  not null,
  goals             text          not null,
  schedule_text     text          not null,
  finish_date       datetime      null,
  stage             int           not null,
  deleted           tinyint(1)    not null,
  NGO_id            int           null,
  category_id       int           not null,
  student_id        int           not null,
  constraint studentportal_project_ibfk_2
  foreign key (NGO_id) references studentportal_ngo (id),
  constraint studentportal_project_ibfk_1
  foreign key (category_id) references studentportal_category (id)
);

create table if not exists studentportal_document
(
  id         int auto_increment primary key,
  document   varchar(100) not null,
  name       varchar(100) not null,
  date_added datetime     not null,
  category   int          not null,
  project_id int          not null,
  constraint studentportal_document_ibfk_1
  foreign key (project_id) references studentportal_project (id)
);

create index project_id
  on studentportal_document (project_id);

create table if not exists studentportal_feedback
(
  project_id   int  not null primary key,
  hours        int  not null,
  achievements text not null,
  experience   int  not null,
  constraint studentportal_feedback_ibfk_1
  foreign key (project_id) references studentportal_project (id)
);

create index NGO_id
  on studentportal_project (NGO_id);

create index category_id
  on studentportal_project (category_id);

create index student_id
  on studentportal_project (student_id);

create table if not exists supervisor_diff
(
  id         int auto_increment primary key,
  diff_type  int      not null,
  details    text     null,
  `when`     datetime not null,
  person_id  int      null,
  project_id int      null,
  constraint supervisor_diff_ibfk_2
  foreign key (project_id) references studentportal_project (id)
);

create index person_id
  on supervisor_diff (person_id);

create index project_id
  on supervisor_diff (project_id);

create table if not exists supervisor_example
(
  project_id     int      not null primary key,
  date_created   datetime not null,
  likes_count    int      not null,
  comments_count int      not null,
  constraint supervisor_example_ibfk_1
  foreign key (project_id) references studentportal_project (id)
);

create table if not exists supervisor_comment
(
  id           int auto_increment primary key,
  text         varchar(200) not null,
  commentor_id int          not null,
  project_id   int          not null,
  constraint supervisor_comment_ibfk_2
  foreign key (project_id) references supervisor_example (project_id)
);

create index commentor_id
  on supervisor_comment (commentor_id);

create index project_id
  on supervisor_comment (project_id);

create table if not exists supervisor_like
(
  id          int auto_increment primary key,
  liked_by_id int not null,
  project_id  int not null,
  constraint supervisor_like_ibfk_1
  foreign key (project_id) references supervisor_example (project_id)
);

create index liked_by_id
  on supervisor_like (liked_by_id);

create index project_id
  on supervisor_like (project_id);

create table if not exists supervisor_news
(
  id           int auto_increment primary key,
  content      text       not null,
  date_created datetime   not null,
  priority     tinyint(1) not null
);

create table if not exists supervisor_notification
(
  id             int auto_increment primary key,
  noti_type      int          null,
  NGO_name       varchar(200) not null,
  NGO_link       varchar(200) not null,
  NGO_details    text         not null,
  NGO_sugg_by_id int          null,
  project_id     int          null,
  constraint supervisor_notification_ibfk_2
  foreign key (project_id) references studentportal_project (id)
);

create index NGO_sugg_by_id
  on supervisor_notification (NGO_sugg_by_id);

create index project_id
  on supervisor_notification (project_id);

create table if not exists supervisor_ta
(
  id         int auto_increment
    primary key,
  email      varchar(100) not null,
  instructor tinyint(1)   not null
);


