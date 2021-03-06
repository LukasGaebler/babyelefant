GRANT USAGE ON SCHEMA public TO babyelefant;

-- public.u_users definition

-- Drop table

-- DROP TABLE public.u_users;

CREATE TABLE public.u_users (
	u_id serial NOT NULL,
	u_name text NOT NULL,
	u_pwd text NOT NULL,
	u_isadmin bool NOT NULL DEFAULT false,
	CONSTRAINT u_users_pkey PRIMARY KEY (u_id)
);


-- public.e_events definition

-- Drop table

-- DROP TABLE public.e_events;

CREATE TABLE public.e_events (
	e_id serial NOT NULL,
	e_name text NOT NULL,
	e_u_user int4 NOT NULL,
	e_adress varchar(255) NULL,
	CONSTRAINT e_events_pkey PRIMARY KEY (e_id),
	CONSTRAINT fk_events_users FOREIGN KEY (e_u_user) REFERENCES u_users(u_id)
);


-- public.c_cameras definition

-- Drop table

-- DROP TABLE public.c_cameras;

CREATE TABLE public.c_cameras (
	c_id serial NOT NULL,
	c_link text NOT NULL,
	c_e_event int4 NOT NULL,
	c_homography jsonb NOT NULL,
	c_maxdistance numeric NOT NULL,
	c_pixelpermeter numeric NOT NULL,
	c_public bool NOT NULL,
	c_downtime_start varchar(5) NOT NULL DEFAULT '20:00',
	c_downtime_end varchar(5) NOT NULL DEFAULT '07:00',
	CONSTRAINT c_cameras_pkey PRIMARY KEY (c_id),
	CONSTRAINT fk_cameras_events FOREIGN KEY (c_e_event) REFERENCES e_events(e_id)
);


-- public.co_contacts definition

-- Drop table

-- DROP TABLE public.co_contacts;

CREATE TABLE public.co_contacts (
	co_p_person1 int4 NOT NULL,
	co_p_person2 int4 NOT NULL,
	co_distance numeric(10,2) NOT NULL,
	co_datetime timestamptz NOT NULL,
	co_camera int4 NOT NULL,
	co_id serial NOT NULL,
	co_p_person2_mask bool NULL,
	co_p_person1_mask bool NULL,
	CONSTRAINT co_contacts2_pkey PRIMARY KEY (co_id, co_datetime, co_camera),
	CONSTRAINT co_contacts_fk FOREIGN KEY (co_camera) REFERENCES c_cameras(c_id) ON UPDATE CASCADE ON DELETE SET NULL
);
CREATE INDEX co_contacts2_co_camera_co_datetime_idx ON public.co_contacts USING btree (co_camera, co_datetime DESC);
CREATE INDEX co_contacts2_co_datetime_idx ON public.co_contacts USING btree (co_datetime DESC);
/* 
select create_hypertable('co_contacts', 'co_datetime', 'co_id', 3, chunk_time_interval => interval '1 day' ); */

/* CREATE MATERIALIZED  VIEW d_distancedata WITH (timescaledb.continuous) as
 SELECT time_bucket('00:05:00'::interval, co_contacts.co_datetime) AS d_datetime,
    avg(co_contacts.co_distance) AS d_avg,
    min(co_contacts.co_distance) AS d_min,
    max(co_contacts.co_distance) AS d_max,
    count(co_contacts.co_p_person1) + count(co_contacts.co_p_person2) AS d_numberofpeople,
    co_contacts.co_camera AS d_c_id,
    (count(
        CASE
            WHEN co_contacts.co_p_person1_mask THEN 1
            ELSE NULL::integer
        END) + count(
        CASE
            WHEN co_contacts.co_p_person2_mask THEN 1
            ELSE NULL::integer
        END)) / NULLIF(count(
        CASE
            WHEN co_contacts.co_p_person1_mask IS NOT NULL THEN 1
            ELSE NULL::integer
        END) + count(
        CASE
            WHEN co_contacts.co_p_person2_mask IS NOT NULL THEN 1
            ELSE NULL::integer
        END), 0) * 100.0 AS d_maskratio
   FROM co_contacts
  GROUP BY (time_bucket('00:05:00'::interval, co_contacts.co_datetime)), co_contacts.co_camera;

SELECT add_continuous_aggregate_policy('d_distancedata',
    start_offset => INTERVAL '4 h',
    end_offset => INTERVAL '1 h',
    schedule_interval => INTERVAL '1 h'); */
    
CREATE TABLE public.d_distancedata (
	d_min numeric(10,2) NOT NULL,
	d_avg numeric(10,2) NOT NULL,
	d_numberofpeople int4 NOT NULL,
	d_c_id int4 NOT NULL,
    d_datetime timestamptz not null,
    d_maskedpeople int4 NOT NULL 
);

create view d_distancedataperevent as  SELECT d_distancedata.d_datetime,
    avg(d_distancedata.d_avg) AS d_avg,
    min(d_distancedata.d_min) AS d_min,
    sum(d_distancedata.d_numberofpeople) AS d_numberofpeople,
    c_cameras.c_e_event AS d_e_event,
    sum(d_distancedata.d_maskedpeople) AS d_maskedpeople
   FROM d_distancedata
     JOIN c_cameras ON d_distancedata.d_c_id = c_cameras.c_id
  GROUP BY c_cameras.c_e_event, d_distancedata.d_datetime;

INSERT INTO public.u_users
(u_id, u_name, u_pwd, u_isadmin)
VALUES(1, 'babyelefant', '$2a$12$wAxP6SHhTfVKTJvXnJliS.3ql7imfi4EsE8tJR0OTXDo2aDrJBp2y', true);

INSERT INTO public.e_events
(e_id, e_name, e_u_user, e_adress)
VALUES(1, 'Street view', 1, 'Test 1');
INSERT INTO public.e_events
(e_id, e_name, e_u_user, e_adress)
VALUES(2, 'HTL Spengergasse', 1, 'Test 1');

/* INSERT INTO public.c_cameras
(c_link, c_e_event, c_homography, c_maxdistance, c_pixelpermeter, c_public, c_downtime_start, c_downtime_end)
VALUES('https://www.youtube.com/watch?v=PGrq-2mju2s', 1, '{"matrix": [[-5.290478678272303e-05, 0.06991421058208373, -1.1505644086773635e-08], [-0.0012537249814707427, 0.5234823163407988, -1.8794378461412196e-08], [-8.847374582763141e-07, 0.000369414680936358, 0.00021879833289292772]]}'::jsonb, 2, 0.1, true, '20:00', '06:00'); */
INSERT INTO public.c_cameras
(c_link, c_e_event, c_homography, c_maxdistance, c_pixelpermeter, c_public, c_downtime_start, c_downtime_end)
VALUES('https://www.youtube.com/watch?v=RQA5RcIZlAM', 1, '{"matrix": [[0.05771778434621434, 0.5908319810460522, -0.0001257312093049082], [0.07848052584723673, 1.1903442117258645, -0.0002832060046981562], [0.00003547530943222285, 0.0005380676134105854, 0.015694877842639343]]}'::jsonb, 4, 3.1281085438109697, false, '20:00', '06:00'); 
INSERT INTO public.c_cameras
(c_link, c_e_event, c_homography, c_maxdistance, c_pixelpermeter, c_public, c_downtime_start, c_downtime_end)
VALUES('https://www.youtube.com/watch?v=RQA5RcIZlAM', 2, '{"matrix": [[0.05771778434621434, 0.5908319810460522, -0.0001257312093049082], [0.07848052584723673, 1.1903442117258645, -0.0002832060046981562], [0.00003547530943222285, 0.0005380676134105854, 0.015694877842639343]]}'::jsonb, 4, 3.1281085438109697, false, '20:00', '06:00'); 