-- On P1:
CREATE DATABASE CS457_PA4;
USE CS457_PA4;
create table Flights (seat int, status int);
insert into Flights values (22,0); -- seat 22 is available
insert into Flights values (23,1); -- seat 23 is occupied
begin transaction;
update flights set status = 1 where seat = 22;

-- On P1:
--commit; --persist the change to disk
--select * from Flights;

-- Expected output

-- Database CS457_PA4 created.
-- Using database CS457_PA4.
-- Table Flights created.
-- 1 new record inserted.
-- 1 new record inserted.
-- Transaction starts.
-- 1 record modified.

-- Transaction committed.
-- seat int|status int
-- 22|1
-- 23|1