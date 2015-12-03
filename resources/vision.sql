alter table vision_trialparam modify column `road_marks` varchar(40) NOT NULL;

alter table vision_trialparam modify column `eccent` double precision;
alter table vision_trial modify column `resp_cost` double precision NOT NULL;
alter table vision_block modify column `ee` double precision;
alter table vision_trial modify column `target_road` varchar(40);

alter table vision_demo add column `time_cost` double precision NOT NULL;
alter table vision_demo drop column end_time;

/* 2015-12-3 */
alter table vision_trialparam add column `step_scheme` varchar(1) NOT NULL;