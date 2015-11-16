alter table vision_trialparam modify column `road_marks` varchar(40) NOT NULL;

alter table vision_trialparam modify column `eccent` double precision;
alter table vision_trial modify column `resp_cost` double precision NOT NULL;
alter table vision_block modify column `ee` double precision;
alter table vision_trial modify column `target_road` varchar(40);