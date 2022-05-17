-- python3.10 pa4.py -f P2.sql

-- On P2:
USE CS457_PA4;
select * from Flights;
begin transaction;
update flights set status = 1 where seat = 22;
commit; --there should be nothing to commit; it's an "abort"
select * from Flights;

-- On P2:
-- select * from Flights;


-- Expected output

-- Using database CS457_PA4.
-- seat int|status int
-- 22|0
-- 23|1
-- Transaction starts.
-- Error: Table Flights is locked!
-- Transaction abort.
-- seat int|status int
-- 22|0
-- 23|1

-- seat int|status int
-- 22|1
-- 23|1