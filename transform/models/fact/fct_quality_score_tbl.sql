{{ config(materialized='table') }}

-- select 
-- source_hashtag,
-- cnt,
-- posts,
-- round(100.0 * cnt / posts, 2) quality_score
-- from (
-- select source_hashtag,
--        count(*) as posts,
--        sum(case when passed_quality_check = True then 1 else null end) as cnt
-- from {{ ref('fct_post_quality') }}
-- group by 1
-- ) a
-- order by quality_score desc

----------
select 
source_hashtag,
posts,
round(100.0 * original / posts, 2) pct_original,
round(100.0 * not_stuffed /posts , 2) pct_not_stuffed,
round(100.0 * on_topic / posts, 2) pct_on_topic,
round(100.0 * passed_qc / posts, 2) quality_score
from (
select source_hashtag,
       count(*) as posts,
       sum(case when passed_quality_check = True then 1 else 0 end) as passed_qc,
       sum(case when is_original = true then 1 else 0 end) original,
       sum(case when is_not_stuffed = true then 1 else 0 end) not_stuffed,
       sum(case when is_on_topic = true then 1 else 0 end) on_topic
--      round(100.0 * avg(is_original::int), 1)    as pct_original,
--      round(100.0 * avg(is_not_stuffed::int), 1) as pct_not_stuffed,
--      round(100.0 * avg(is_on_topic::int), 1)    as pct_on_topic
from dbt_dev.fct_post_quality
group by 1
order by 3
) a