
INSERT INTO u_users (u_id, u_name, u_pwd, u_isadmin) VALUES(1, 'admin', '$2a$12$wAxP6SHhTfVKTJvXnJliS.3ql7imfi4EsE8tJR0OTXDo2aDrJBp2y', true);
INSERT INTO e_events (e_id, e_name, e_u_user, e_adress) VALUES(1, 'Test', 1, 'Test 1');
INSERT INTO c_cameras (c_link, c_e_event, c_homography, c_maxdistance, c_pixelpermeter, c_public, c_downtime_start, c_downtime_end) VALUES('0', 1, '{"matrix": [[-5.290478678272303e-05, 0.06991421058208373, -1.1505644086773635e-08], [-0.0012537249814707427, 0.5234823163407988, -1.8794378461412196e-08], [-8.847374582763141e-07, 0.000369414680936358, 0.00021879833289292772]]}', 2, 1, true, '20:00', '06:00'); 