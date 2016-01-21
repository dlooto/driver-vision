alter table vision_trialparam modify column `road_marks` varchar(40) NOT NULL;

alter table vision_trialparam modify column `eccent` double precision;
alter table vision_trial modify column `resp_cost` double precision NOT NULL;
alter table vision_block modify column `ee` double precision;
alter table vision_trial modify column `target_road` varchar(40);

alter table vision_demo add column `time_cost` double precision NOT NULL;
alter table vision_demo drop column end_time;

/* 2015-12-3 */
alter table vision_trialparam add column `step_scheme` varchar(1) NOT NULL;

/* 2015-12-16 */
alter table vision_trialparam modify column `eccent` varchar(40);
alter table vision_trialparam modify column `init_angle` varchar(40);

/* 2015-12-17 */
alter table vision_trialparam add column `board_scale` double precision;
alter table vision_trialparam add column `board_range` varchar(1);
alter table vision_trialparam add column `board_space` double precision;

alter table vision_trialparam drop column `road_num`;
alter table vision_trialparam modify column `road_marks` varchar(100) NOT NULL;

/* 2015-12-25 Christmas */
alter table vision_trialparam add column `pre_board_num` integer;

/* 2015-12-28 */
alter table vision_block modify column `S` varchar(40);

/* 2015-12-30 */
alter table vision_block modify column `tseat` varchar(10) NOT NULL;

/* 2015-1-9 */
alter table vision_trialparam add column `velocity` varchar(40);
alter table vision_trialparam add column `wp_scheme` varchar(1);

/* 2016-1-19 */
alter table vision_trialparam modify column `step_scheme` varchar(4) NOT NULL;
alter table vision_trialparam add column `space_type` varchar(4);
alter table vision_block modify column `cate` varchar(4) NOT NULL;
alter table vision_trial modify column `cate` varchar(4) NOT NULL;

/* 2016-1-21 */
alter table vision_trialparam add column `space_scale_type` varchar(4);




