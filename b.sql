insert into `group` (id, name, description) values (1, 'StandPipe', 'This is the StandPipe group');
insert into `group` (id, name, description) values (2, 'Highgate', 'This is the Highgate group');
insert into `group` (id, name, description) values (3, 'Papine', 'This is the Papine group');
insert into `group` (id, name, description) values (9, 'Default Group', 'This is the Default group');

insert into `user_role` (id, name, description) values (1, 'Default Role', 'This is the default role');
insert into `user_role` (id, name, description) values (2, 'Interviewer', 'This is the Interviewer');
insert into `user_role` (id, name, description) values (3, 'Officer', 'This is the Officer');
insert into `user_role` (id, name, description) values (4, 'Admin', 'This is the Admin');


insert into `dimensions` (name, description) values ('General', 'This is the description for a General Question');
insert into `dimensions` (name, description) values ('Dimension 1', 'This is the description for Dimension 1');
insert into `dimensions` (name, description) values ('Dimension 2', 'This is the description for Dimension 2');
insert into `dimensions` (name, description) values ('Dimension 3', 'This is the description for Dimension 3');
insert into `dimensions` (name, description) values ('Dimension 4', 'This is the description for Dimension 4');


insert into `question_type` (name, code) values('Simple Question', 1);
insert into `question_type` (name, code) values('Yes or No', 2);
insert into `question_type` (name, code) values('Scaled Questions', 3);
insert into `question_type` (name, code) values('Choice Questions', 4);
